/** Metadatos visuales de los tipos de documento (carpetas). */
import type { DocumentType } from '$lib/api/types';

export const DOC_TYPE_LABEL: Record<DocumentType, string> = {
  manual: 'Manuales',
  certificate: 'Certificados',
  report: 'Reportes',
  standard: 'Normas',
  invoice: 'Facturas',
  life_sheet: 'Hoja de vida',
  photo: 'Fotos',
  signature: 'Firmas',
  tecnovigilancia: 'Tecnovigilancia',
  other: 'Otros',
};

/** Orden de las carpetas en el detalle del equipo. */
export const DOC_TYPE_ORDER: DocumentType[] = [
  'manual',
  'tecnovigilancia',
  'certificate',
  'standard',
  'report',
  'invoice',
  'photo',
  'signature',
  'life_sheet',
  'other',
];

/** Tipos que un usuario puede elegir al subir un documento a un equipo. */
export const EQUIPMENT_DOC_TYPES: DocumentType[] = [
  'manual',
  'tecnovigilancia',
  'certificate',
  'standard',
  'report',
  'invoice',
  'other',
];

export const EQUIPMENT_DOC_TYPE_OPTIONS = EQUIPMENT_DOC_TYPES.map((value) => ({
  value,
  label: DOC_TYPE_LABEL[value],
}));

export function docTypeLabel(type: DocumentType): string {
  return DOC_TYPE_LABEL[type] ?? type;
}
