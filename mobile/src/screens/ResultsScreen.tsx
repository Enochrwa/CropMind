import React, { useState } from 'react';
import {
  View, Text, ScrollView, TouchableOpacity, StyleSheet,
  Linking, Alert,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useTranslation } from 'react-i18next';
import { useAppStore } from '../store';

const SEVERITY_COLORS: Record<string, string> = {
  none: '#4ade80',
  low: '#a3e635',
  medium: '#fbbf24',
  high: '#f97316',
  critical: '#ef4444',
};

export default function ResultsScreen() {
  const { t } = useTranslation();
  const router = useRouter();
  const { currentDiagnosis } = useAppStore();
  const [activeTab, setActiveTab] = useState<'treatment' | 'suppliers' | 'market'>('treatment');

  if (!currentDiagnosis) {
    router.replace('/camera');
    return null;
  }

  const { result, cost_rwf, balance_remaining } = currentDiagnosis;
  const severityColor = SEVERITY_COLORS[result.severity] || '#fbbf24';

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Header */}
      <View style={styles.header}>
        <View style={[styles.severityBadge, { backgroundColor: severityColor + '22', borderColor: severityColor }]}>
          <Text style={[styles.severityText, { color: severityColor }]}>
            {t(`severity.${result.severity}`)}
          </Text>
        </View>
        <Text style={styles.diseaseName}>{result.disease_display_name}</Text>
        <Text style={styles.confidence}>
          {Math.round(result.confidence * 100)}% confidence
        </Text>
        <Text style={styles.description}>{result.description}</Text>

        {result.severity !== 'none' && (
          <View style={styles.urgencyBox}>
            <Text style={styles.urgencyIcon}>⚠️</Text>
            <Text style={styles.urgencyText}>{result.urgency_message}</Text>
          </View>
        )}
      </View>

      {/* Tabs */}
      <View style={styles.tabs}>
        {(['treatment', 'suppliers', 'market'] as const).map((tab) => (
          <TouchableOpacity
            key={tab}
            style={[styles.tab, activeTab === tab && styles.tabActive]}
            onPress={() => setActiveTab(tab)}
          >
            <Text style={[styles.tabText, activeTab === tab && styles.tabTextActive]}>
              {tab === 'treatment' ? '💊 Treatment' :
               tab === 'suppliers' ? '🏪 Suppliers' : '💰 Prices'}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Treatment Tab */}
      {activeTab === 'treatment' && (
        <View style={styles.section}>
          {result.treatment_steps.map((step) => (
            <View key={step.step} style={styles.stepCard}>
              <View style={styles.stepNum}>
                <Text style={styles.stepNumText}>{step.step}</Text>
              </View>
              <View style={styles.stepBody}>
                <Text style={styles.stepAction}>{step.action}</Text>
                {step.product && (
                  <Text style={styles.stepProduct}>Product: {step.product}</Text>
                )}
                {step.timing && (
                  <Text style={styles.stepTiming}>⏱ {step.timing}</Text>
                )}
              </View>
            </View>
          ))}

          <Text style={styles.sectionTitle}>Prevention Tips</Text>
          {result.prevention_tips.map((tip, i) => (
            <View key={i} style={styles.tipRow}>
              <Text style={styles.tipBullet}>✓</Text>
              <Text style={styles.tipText}>{tip}</Text>
            </View>
          ))}
        </View>
      )}

      {/* Suppliers Tab */}
      {activeTab === 'suppliers' && (
        <View style={styles.section}>
          {result.suppliers.length === 0 ? (
            <Text style={styles.emptyText}>No suppliers found nearby. Enable location for better results.</Text>
          ) : (
            result.suppliers.map((s) => (
              <View key={s.id} style={styles.supplierCard}>
                <View style={styles.supplierHeader}>
                  <Text style={styles.supplierName}>{s.name}</Text>
                  {s.is_verified && <Text style={styles.verifiedBadge}>✓ Verified</Text>}
                </View>
                <Text style={styles.supplierDist}>📍 {s.distance_km} km away</Text>
                {s.address && <Text style={styles.supplierAddr}>{s.address}</Text>}
                <View style={styles.supplierActions}>
                  {s.phone && (
                    <TouchableOpacity
                      style={styles.callBtn}
                      onPress={() => Linking.openURL(`tel:${s.phone}`)}
                    >
                      <Text style={styles.callBtnText}>📞 Call</Text>
                    </TouchableOpacity>
                  )}
                  {s.whatsapp && (
                    <TouchableOpacity
                      style={styles.waBtn}
                      onPress={() => Linking.openURL(`https://wa.me/${s.whatsapp}`)}
                    >
                      <Text style={styles.waBtnText}>💬 WhatsApp</Text>
                    </TouchableOpacity>
                  )}
                </View>
              </View>
            ))
          )}
        </View>
      )}

      {/* Market Prices Tab */}
      {activeTab === 'market' && (
        <View style={styles.section}>
          {result.market_prices.map((p, i) => (
            <View key={i} style={styles.priceCard}>
              <Text style={styles.priceCrop}>{p.crop.toUpperCase()}</Text>
              <Text style={styles.priceMain}>{p.price_per_kg_rwf.toLocaleString()} RWF/kg</Text>
              <Text style={styles.priceUsd}>${p.price_per_kg_usd.toFixed(3)}/kg</Text>
              <Text style={styles.priceMarket}>{p.market}</Text>
              <Text style={styles.priceDate}>Updated: {p.updated_at}</Text>
            </View>
          ))}
        </View>
      )}

      {/* Footer */}
      <View style={styles.footer}>
        <Text style={styles.footerCost}>Cost: {cost_rwf} RWF · Balance: {balance_remaining.toFixed(0)} RWF</Text>
        <TouchableOpacity style={styles.newScanBtn} onPress={() => router.replace('/camera')}>
          <Text style={styles.newScanText}>📷 Scan Another</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0a0a0f' },
  content: { padding: 20, paddingBottom: 40 },
  header: { marginBottom: 20 },
  severityBadge: {
    alignSelf: 'flex-start', paddingHorizontal: 12, paddingVertical: 5,
    borderRadius: 99, borderWidth: 1, marginBottom: 10,
  },
  severityText: { fontSize: 12, fontWeight: '700', letterSpacing: 0.5 },
  diseaseName: { fontSize: 26, fontWeight: '700', color: '#f4f4ff', marginBottom: 4 },
  confidence: { fontSize: 13, color: '#7070a0', marginBottom: 12 },
  description: { fontSize: 14, color: '#c0c0d0', lineHeight: 21, marginBottom: 12 },
  urgencyBox: {
    flexDirection: 'row', alignItems: 'flex-start', gap: 8,
    backgroundColor: 'rgba(255,107,53,.1)', borderWidth: 1,
    borderColor: 'rgba(255,107,53,.3)', borderRadius: 10, padding: 12,
  },
  urgencyIcon: { fontSize: 16 },
  urgencyText: { flex: 1, color: '#ff6b35', fontSize: 13, lineHeight: 20 },
  tabs: { flexDirection: 'row', gap: 6, marginBottom: 20 },
  tab: {
    flex: 1, paddingVertical: 10, borderRadius: 10, alignItems: 'center',
    backgroundColor: '#111118', borderWidth: 1, borderColor: '#1e1e2e',
  },
  tabActive: { backgroundColor: 'rgba(0,229,160,.1)', borderColor: 'rgba(0,229,160,.4)' },
  tabText: { fontSize: 12, color: '#7070a0', fontWeight: '600' },
  tabTextActive: { color: '#00e5a0' },
  section: { gap: 12 },
  stepCard: {
    flexDirection: 'row', gap: 14,
    backgroundColor: '#111118', borderRadius: 12,
    borderWidth: 1, borderColor: '#1e1e2e', padding: 14,
  },
  stepNum: {
    width: 32, height: 32, borderRadius: 16,
    backgroundColor: 'rgba(0,229,160,.15)', alignItems: 'center', justifyContent: 'center',
  },
  stepNumText: { color: '#00e5a0', fontWeight: '700', fontSize: 14 },
  stepBody: { flex: 1, gap: 4 },
  stepAction: { color: '#e8e8f0', fontSize: 14, fontWeight: '500', lineHeight: 20 },
  stepProduct: { color: '#a78bfa', fontSize: 12 },
  stepTiming: { color: '#7070a0', fontSize: 12 },
  sectionTitle: { color: '#f4f4ff', fontSize: 16, fontWeight: '700', marginTop: 8, marginBottom: 4 },
  tipRow: { flexDirection: 'row', gap: 10, alignItems: 'flex-start' },
  tipBullet: { color: '#00e5a0', fontSize: 14, marginTop: 1 },
  tipText: { flex: 1, color: '#c0c0d0', fontSize: 13, lineHeight: 20 },
  supplierCard: {
    backgroundColor: '#111118', borderRadius: 12,
    borderWidth: 1, borderColor: '#1e1e2e', padding: 14, gap: 6,
  },
  supplierHeader: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  supplierName: { flex: 1, color: '#f4f4ff', fontSize: 15, fontWeight: '600' },
  verifiedBadge: {
    fontSize: 10, color: '#00e5a0', backgroundColor: 'rgba(0,229,160,.1)',
    paddingHorizontal: 8, paddingVertical: 3, borderRadius: 99,
  },
  supplierDist: { color: '#7070a0', fontSize: 12 },
  supplierAddr: { color: '#7070a0', fontSize: 12 },
  supplierActions: { flexDirection: 'row', gap: 8, marginTop: 4 },
  callBtn: {
    flex: 1, backgroundColor: 'rgba(56,189,248,.1)', borderWidth: 1,
    borderColor: 'rgba(56,189,248,.3)', borderRadius: 8, padding: 8, alignItems: 'center',
  },
  callBtnText: { color: '#38bdf8', fontSize: 13, fontWeight: '600' },
  waBtn: {
    flex: 1, backgroundColor: 'rgba(74,222,128,.1)', borderWidth: 1,
    borderColor: 'rgba(74,222,128,.3)', borderRadius: 8, padding: 8, alignItems: 'center',
  },
  waBtnText: { color: '#4ade80', fontSize: 13, fontWeight: '600' },
  priceCard: {
    backgroundColor: '#111118', borderRadius: 12,
    borderWidth: 1, borderColor: '#1e1e2e', padding: 16, gap: 4,
  },
  priceCrop: { color: '#7070a0', fontSize: 11, letterSpacing: 0.1, fontWeight: '700' },
  priceMain: { color: '#fbbf24', fontSize: 22, fontWeight: '700' },
  priceUsd: { color: '#7070a0', fontSize: 13 },
  priceMarket: { color: '#c0c0d0', fontSize: 13 },
  priceDate: { color: '#3a3a5c', fontSize: 11 },
  emptyText: { color: '#7070a0', textAlign: 'center', marginTop: 40, fontSize: 14 },
  footer: {
    marginTop: 24, alignItems: 'center', gap: 12,
    paddingTop: 20, borderTopWidth: 1, borderTopColor: '#1e1e2e',
  },
  footerCost: { color: '#3a3a5c', fontSize: 12 },
  newScanBtn: {
    backgroundColor: '#00e5a0', paddingHorizontal: 32, paddingVertical: 14,
    borderRadius: 99, width: '100%', alignItems: 'center',
  },
  newScanText: { color: '#000', fontWeight: '700', fontSize: 15 },
});
