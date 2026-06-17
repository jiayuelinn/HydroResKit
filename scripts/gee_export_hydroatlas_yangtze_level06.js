// Earth Engine export template for HydroResKit.
//
// Paste this script into the Google Earth Engine Code Editor after checking
// HydroATLAS/HydroSHEDS terms. It exports the HydroATLAS level 6 attributes
// needed by the initial HydroResKit mapping for the Yangtze main basin.
//
// Dataset catalog:
// https://developers.google.com/earth-engine/datasets/catalog/WWF_HydroATLAS_v1_Basins_level06

var basins = ee.FeatureCollection('WWF/HydroATLAS/v1/Basins/level06');
var yangtzeMainBas = 4060009880;

var columns = [
  'HYBAS_ID',
  'MAIN_BAS',
  'pre_mm_s01', 'pre_mm_s02', 'pre_mm_s03', 'pre_mm_s04',
  'pre_mm_s05', 'pre_mm_s06', 'pre_mm_s07', 'pre_mm_s08',
  'pre_mm_s09', 'pre_mm_s10', 'pre_mm_s11', 'pre_mm_s12',
  'cmi_ix_syr',
  'inu_pc_slt',
  'ppd_pk_sav',
  'urb_pc_sse',
  'crp_pc_sse',
  'slp_dg_sav',
  'for_pc_sse',
  'pet_mm_syr',
  'aet_mm_syr',
  'lka_pc_sse',
  'wet_pc_sg1',
  'wet_pc_sg2',
  'gdp_ud_sav'
];

var yangtze = basins
  .filter(ee.Filter.eq('MAIN_BAS', yangtzeMainBas))
  .select(columns);

print('Yangtze HydroATLAS level 6 feature count', yangtze.size());
print('Example feature', yangtze.first());

Export.table.toDrive({
  collection: yangtze,
  description: 'hydroatlas_yangtze_level06_hydroreskit',
  fileNamePrefix: 'hydroatlas_yangtze_level06_hydroreskit',
  fileFormat: 'CSV',
  selectors: columns
});
