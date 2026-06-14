import React, { useState, useRef, useCallback, useEffect } from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet, ActivityIndicator,
  Alert, Platform,
} from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import * as ImageManipulator from 'expo-image-manipulator';
import * as Location from 'expo-location';
import { useRouter } from 'expo-router';
import { useTranslation } from 'react-i18next';

import { useOnDeviceModel } from '../hooks/useOnDeviceModel';
import { diagnoseApi } from '../services/api';
import { useAppStore } from '../store';

const CROP_TYPES = ['tomato', 'potato', 'corn', 'apple', 'bean', 'cassava', 'other'];

export default function CameraScreen() {
  const { t } = useTranslation();
  const router = useRouter();
  const { user, language, setCurrentDiagnosis } = useAppStore();

  const cameraRef = useRef<CameraView>(null);
  const [permission, requestPermission] = useCameraPermissions();
  const [isCaptured, setIsCaptured] = useState(false);
  const [selectedCrop, setSelectedCrop] = useState('tomato');
  const [phase, setPhase] = useState<'idle' | 'capturing' | 'detecting' | 'enriching'>('idle');

  const { isReady, loadModel, predict } = useOnDeviceModel();

  useEffect(() => { loadModel(); }, [loadModel]);

  const handleCapture = useCallback(async () => {
    if (!cameraRef.current || phase !== 'idle') return;

    setPhase('capturing');
    try {
      // Capture
      const photo = await cameraRef.current.takePictureAsync({ quality: 0.7, base64: false });
      if (!photo) throw new Error('No photo captured');

      // Resize to 512px for faster processing
      const resized = await ImageManipulator.manipulateAsync(
        photo.uri,
        [{ resize: { width: 512 } }],
        { compress: 0.8, format: ImageManipulator.SaveFormat.JPEG }
      );

      setPhase('detecting');
      // On-device prediction (offline)
      const prediction = await predict(resized.uri);
      if (!prediction) throw new Error('Detection failed');

      if (prediction.confidence < 0.5) {
        Alert.alert(
          'Low confidence',
          'Image unclear. Please retake with better lighting.',
          [{ text: 'Retake', onPress: () => setPhase('idle') }]
        );
        return;
      }

      // Get location for supplier lookup
      let latitude: number | undefined;
      let longitude: number | undefined;
      try {
        const loc = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.Balanced });
        latitude = loc.coords.latitude;
        longitude = loc.coords.longitude;
      } catch {}

      setPhase('enriching');
      // Server enrichment (requires balance + internet)
      const result = await diagnoseApi.enrich({
        device_prediction: prediction.label,
        device_confidence: prediction.confidence,
        crop_type: selectedCrop,
        latitude,
        longitude,
        language,
      });

      setCurrentDiagnosis(result);
      router.push('/results');
    } catch (err: any) {
      const msg = err?.response?.data?.detail || err.message || t('errors.generic');
      Alert.alert('Error', msg);
      setPhase('idle');
    }
  }, [phase, selectedCrop, predict, language, router, setCurrentDiagnosis, t]);

  if (!permission) return <View />;
  if (!permission.granted) {
    return (
      <View style={styles.center}>
        <Text style={styles.permText}>{t('errors.camera')}</Text>
        <TouchableOpacity style={styles.btn} onPress={requestPermission}>
          <Text style={styles.btnText}>Grant Permission</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const isProcessing = phase !== 'idle';

  return (
    <View style={styles.container}>
      <CameraView ref={cameraRef} style={styles.camera} facing="back">
        {/* Crop selector */}
        <View style={styles.cropRow}>
          {CROP_TYPES.map((crop) => (
            <TouchableOpacity
              key={crop}
              style={[styles.cropChip, selectedCrop === crop && styles.cropChipActive]}
              onPress={() => setSelectedCrop(crop)}
            >
              <Text style={[styles.cropChipText, selectedCrop === crop && styles.cropChipTextActive]}>
                {crop}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Viewfinder */}
        <View style={styles.viewfinder} pointerEvents="none" />

        {/* Status */}
        {isProcessing && (
          <View style={styles.statusBar}>
            <ActivityIndicator color="#00e5a0" />
            <Text style={styles.statusText}>
              {phase === 'detecting' ? t('camera.analyzing') :
               phase === 'enriching' ? 'Getting treatment plan...' :
               t('camera.scanning')}
            </Text>
          </View>
        )}

        {/* Capture button */}
        <View style={styles.captureRow}>
          <TouchableOpacity
            style={[styles.captureBtn, isProcessing && styles.captureBtnDisabled]}
            onPress={handleCapture}
            disabled={isProcessing || !isReady}
          >
            <View style={styles.captureBtnInner} />
          </TouchableOpacity>
        </View>

        {/* Balance indicator */}
        <View style={styles.balanceChip}>
          <Text style={styles.balanceText}>⚡ {user?.balance_rwf?.toFixed(0) || 0} RWF</Text>
        </View>
      </CameraView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#000' },
  camera: { flex: 1 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#0a0a0f', padding: 24 },
  permText: { color: '#e8e8f0', fontSize: 16, textAlign: 'center', marginBottom: 20 },
  btn: { backgroundColor: '#00e5a0', paddingHorizontal: 24, paddingVertical: 12, borderRadius: 99 },
  btnText: { color: '#000', fontWeight: '700' },
  cropRow: {
    position: 'absolute', top: 60, left: 0, right: 0,
    flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'center',
    gap: 6, paddingHorizontal: 12,
  },
  cropChip: {
    paddingHorizontal: 12, paddingVertical: 5, borderRadius: 99,
    backgroundColor: 'rgba(0,0,0,0.5)', borderWidth: 1, borderColor: 'rgba(255,255,255,0.2)',
  },
  cropChipActive: { backgroundColor: '#00e5a0', borderColor: '#00e5a0' },
  cropChipText: { color: '#fff', fontSize: 12, fontWeight: '500' },
  cropChipTextActive: { color: '#000' },
  viewfinder: {
    position: 'absolute', top: '25%', left: '10%', right: '10%', bottom: '25%',
    borderWidth: 2, borderColor: 'rgba(0,229,160,0.6)', borderRadius: 12,
  },
  statusBar: {
    position: 'absolute', bottom: 140, left: 0, right: 0,
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 10,
    backgroundColor: 'rgba(0,0,0,0.7)', paddingVertical: 10,
  },
  statusText: { color: '#00e5a0', fontSize: 14, fontWeight: '600' },
  captureRow: {
    position: 'absolute', bottom: 50, left: 0, right: 0,
    alignItems: 'center',
  },
  captureBtn: {
    width: 76, height: 76, borderRadius: 38,
    backgroundColor: 'rgba(255,255,255,0.3)', borderWidth: 3, borderColor: '#fff',
    alignItems: 'center', justifyContent: 'center',
  },
  captureBtnDisabled: { opacity: 0.4 },
  captureBtnInner: { width: 58, height: 58, borderRadius: 29, backgroundColor: '#fff' },
  balanceChip: {
    position: 'absolute', top: 16, right: 16,
    backgroundColor: 'rgba(0,0,0,0.6)', paddingHorizontal: 12, paddingVertical: 6,
    borderRadius: 99, borderWidth: 1, borderColor: 'rgba(0,229,160,0.4)',
  },
  balanceText: { color: '#00e5a0', fontSize: 12, fontWeight: '700' },
});
