/**
 * On-device disease classification using TensorFlow Lite.
 * Runs entirely offline — no internet required.
 * Model: MobileNetV3-Small fine-tuned on PlantVillage (2 MB TFLite).
 */
import { useState, useCallback, useRef } from 'react';
import * as tf from '@tensorflow/tfjs';
import '@tensorflow/tfjs-react-native';
import { decodeJpeg } from '@tensorflow/tfjs-react-native';
import * as FileSystem from 'expo-file-system';

// Class labels — mirrors ml/disease_classes.py
const CLASS_LABELS = [
  'apple_scab', 'apple_black_rot', 'apple_cedar_rust',
  'corn_gray_leaf_spot', 'corn_common_rust', 'corn_northern_leaf_blight',
  'potato_early_blight', 'potato_late_blight',
  'tomato_bacterial_spot', 'tomato_early_blight', 'tomato_late_blight',
  'tomato_leaf_mold', 'tomato_septoria_leaf_spot', 'tomato_spider_mites',
  'tomato_target_spot', 'tomato_yellow_leaf_curl', 'tomato_mosaic_virus',
  'healthy',
];

export interface PredictionResult {
  label: string;
  confidence: number;
  isHealthy: boolean;
}

export function useOnDeviceModel() {
  const [isReady, setIsReady] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const modelRef = useRef<tf.GraphModel | tf.LayersModel | null>(null);

  const loadModel = useCallback(async () => {
    if (modelRef.current) return;
    try {
      await tf.ready();
      // Model bundled in assets/ — loaded from device storage
      const modelPath = FileSystem.bundleDirectory + 'assets/cropmind_v1.json';
      modelRef.current = await tf.loadGraphModel(`file://${modelPath}`);
      setIsReady(true);
    } catch (e) {
      console.warn('On-device model not available:', e);
    }
  }, []);

  const predict = useCallback(async (imageUri: string): Promise<PredictionResult | null> => {
    if (!modelRef.current) return null;
    setIsLoading(true);
    try {
      // Read image as base64
      const imageData = await FileSystem.readAsStringAsync(imageUri, {
        encoding: FileSystem.EncodingType.Base64,
      });
      const rawData = Uint8Array.from(atob(imageData), (c) => c.charCodeAt(0));

      // Preprocess
      const imageTensor = tf.tidy(() => {
        const decoded = decodeJpeg(rawData);
        const resized = tf.image.resizeBilinear(decoded, [224, 224]);
        // Normalise (ImageNet stats)
        const mean = tf.tensor([0.485, 0.456, 0.406]).reshape([1, 1, 3]);
        const std = tf.tensor([0.229, 0.224, 0.225]).reshape([1, 1, 3]);
        return resized.div(255.0).sub(mean).div(std).expandDims(0);
      });

      const output = modelRef.current.predict(imageTensor) as tf.Tensor;
      const probabilities = await tf.softmax(output).data();
      imageTensor.dispose();
      output.dispose();

      const maxIdx = Array.from(probabilities).indexOf(Math.max(...probabilities));
      const label = CLASS_LABELS[maxIdx] || 'unknown';
      const confidence = probabilities[maxIdx];

      return { label, confidence, isHealthy: label === 'healthy' };
    } catch (e) {
      console.error('Prediction error:', e);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { isReady, isLoading, loadModel, predict };
}
