export type Matrix = Record<string, Record<string, boolean>>;

export interface RolesMatrix {
  matrix: Matrix; // rol -> capacidad -> bool
}

export interface ClinicFeaturesMatrix {
  matrix: Matrix; // clinic_id -> feature -> bool
}

export interface MyFeatures {
  features: Record<string, boolean>;
}
