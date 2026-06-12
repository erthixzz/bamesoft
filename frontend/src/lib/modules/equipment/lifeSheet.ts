// Modelo de formulario de la Hoja de Vida. Los campos enlazados directamente a
// inputs se tipan como `string` (no `string | null`) para un binding limpio;
// las cadenas vacías se convierten a null al enviar (ver `nullifyEmpty` en la
// página) y el backend acepta todo como opcional.

export interface Contacto {
  nombre: string;
  telefono: string;
  correo: string;
  pais: string;
}

export interface Componente {
  nombre: string;
  marca: string;
  modelo: string;
  serie: string;
}

export interface Identificacion {
  activo_fijo: string;
  registro_tipo: string; // RS | PC | NR
  registro_numero: string;
  codigo_prestador: string;
  sede: string;
  distintivo: string;
  descripcion: string;
}

export interface Equipo {
  tipo: string;
  referencia_lote: string;
  servicio: string;
  ubicacion_texto: string;
  movilidad: string; // movil | fijo
}

export interface RegistroHistorico {
  forma_adquisicion: string;
  documento_adquisicion: string;
  acta_recibo: string;
  fecha_instalacion: string;
  inicio_operacion: string;
  fecha_fabricacion: string;
  tec_predominante: string[];
  costo: number | null;
  moneda: string;
  vida_util_anios: number | null;
  proveedor: Contacto;
  representante: Contacto;
  fabricante: Contacto;
}

export interface Rangos {
  voltaje: string;
  corriente: string;
  potencia: string;
  humedad: string;
  temperatura: string;
  frecuencia: string;
  presion: string;
  velocidad: string;
}

export interface Tecnico {
  fuente_alimentacion: string[];
  voltaje_max: string;
  voltaje_min: string;
  corriente_max: string;
  corriente_min: string;
  potencia: string;
  frecuencia: string;
  presion: string;
  velocidad: string;
  peso: string;
  temperatura: string;
  otros: string;
  rangos: Rangos;
  accesorios: string;
  recomendaciones: string;
}

export interface ApoyoTecnico {
  manuales: string[];
  planos: string[];
  clas_biomedica: string[];
}

export interface Mantenimiento {
  frec_mantenimiento: string;
  requiere_calibracion: boolean | null;
  frec_calibracion: string;
}

export interface LifeSheetData {
  identificacion: Identificacion;
  equipo: Equipo;
  registro_historico: RegistroHistorico;
  tecnico: Tecnico;
  apoyo_tecnico: ApoyoTecnico;
  componentes: Componente[];
  mantenimiento: Mantenimiento;
}

export interface SharedFields {
  name: string;
  brand: string;
  model: string;
  serial_number: string;
  manufacturer: string;
  risk_class: string; // '' | I | IIa | IIb | III
  status: string; // EquipmentStatus
  location_id: string;
  acquisition_date: string;
  warranty_until: string;
  image_url: string;
  notes: string;
}

export interface ClinicHeader {
  id: string;
  name: string;
  logo_url?: string | null;
}

export interface LifeSheet {
  equipment_id: string;
  code: string;
  formato_codigo: string;
  formato_fecha: string;
  clinic?: ClinicHeader | null;
  shared: SharedFields;
  data: LifeSheetData;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface LifeSheetUpdate {
  data: LifeSheetData;
  formato_codigo?: string | null;
  formato_fecha?: string | null;
  shared: SharedFields;
}

function contacto(): Contacto {
  return { nombre: '', telefono: '', correo: '', pais: '' };
}

/** Estructura vacía para inicializar/normalizar el formulario sin null-checks. */
export function emptyLifeSheetData(): LifeSheetData {
  return {
    identificacion: {
      activo_fijo: '',
      registro_tipo: '',
      registro_numero: '',
      codigo_prestador: '',
      sede: '',
      distintivo: '',
      descripcion: '',
    },
    equipo: {
      tipo: '',
      referencia_lote: '',
      servicio: '',
      ubicacion_texto: '',
      movilidad: '',
    },
    registro_historico: {
      forma_adquisicion: '',
      documento_adquisicion: '',
      acta_recibo: '',
      fecha_instalacion: '',
      inicio_operacion: '',
      fecha_fabricacion: '',
      tec_predominante: [],
      costo: null,
      moneda: 'COP',
      vida_util_anios: null,
      proveedor: contacto(),
      representante: contacto(),
      fabricante: contacto(),
    },
    tecnico: {
      fuente_alimentacion: [],
      voltaje_max: '',
      voltaje_min: '',
      corriente_max: '',
      corriente_min: '',
      potencia: '',
      frecuencia: '',
      presion: '',
      velocidad: '',
      peso: '',
      temperatura: '',
      otros: '',
      rangos: {
        voltaje: '',
        corriente: '',
        potencia: '',
        humedad: '',
        temperatura: '',
        frecuencia: '',
        presion: '',
        velocidad: '',
      },
      accesorios: '',
      recomendaciones: '',
    },
    apoyo_tecnico: { manuales: [], planos: [], clas_biomedica: [] },
    componentes: [],
    mantenimiento: {
      frec_mantenimiento: '',
      requiere_calibracion: null,
      frec_calibracion: '',
    },
  };
}
