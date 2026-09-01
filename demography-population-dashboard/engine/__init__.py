"""
Vital Stats Suite - Demographic Engine Package
"""

from engine.base import (
    DemographicDataset,
    DemographicMeasureResult,
    QualityCheckResult,
    WHO_STANDARD_POPULATION_5YR,
    SEGI_STANDARD_POPULATION_5YR,
)
from engine.sex_composition import (
    calculate_masculinity_proportion,
    calculate_sex_ratio,
    calculate_excess_of_males,
    compute_block_a,
)
from engine.age_dependency import (
    calculate_age_composition_ratio,
    calculate_total_dependency_ratio,
    calculate_child_dependency_ratio,
    calculate_old_age_dependency_ratio,
    compute_block_b,
)
from engine.fertility import (
    calculate_crude_birth_rate,
    calculate_marital_birth_rate,
    calculate_general_fertility_rate,
    calculate_age_specific_fertility_rates,
    calculate_total_fertility_rate,
    calculate_gross_reproduction_rate,
    calculate_net_reproduction_rate,
    compute_block_c,
)
from engine.mortality import (
    calculate_crude_death_rate,
    calculate_corrected_cdr,
    calculate_neonatal_mortality_rate,
    calculate_infant_mortality_rate,
    calculate_child_mortality_rate,
    calculate_age_specific_death_rates,
    calculate_direct_standardized_rate,
    calculate_smr_and_indirect_standardized_rate,
    compute_block_d,
)
from engine.quality import (
    calculate_whipples_index,
    calculate_myers_blended_index,
    calculate_pec_comparison,
    validate_dataset_completeness,
    run_all_quality_checks,
)
from engine.interpretation import (
    interpret_measure,
    BENCHMARK_REGISTRY,
)
from engine.pipeline import (
    DemographicPipelineResult,
    ComparisonResult,
    run_demographic_pipeline,
    compare_two_datasets,
)

__all__ = [
    "DemographicDataset",
    "DemographicMeasureResult",
    "QualityCheckResult",
    "WHO_STANDARD_POPULATION_5YR",
    "SEGI_STANDARD_POPULATION_5YR",
    "calculate_masculinity_proportion",
    "calculate_sex_ratio",
    "calculate_excess_of_males",
    "calculate_age_composition_ratio",
    "calculate_total_dependency_ratio",
    "calculate_child_dependency_ratio",
    "calculate_old_age_dependency_ratio",
    "calculate_crude_birth_rate",
    "calculate_marital_birth_rate",
    "calculate_general_fertility_rate",
    "calculate_age_specific_fertility_rates",
    "calculate_total_fertility_rate",
    "calculate_gross_reproduction_rate",
    "calculate_net_reproduction_rate",
    "calculate_crude_death_rate",
    "calculate_corrected_cdr",
    "calculate_neonatal_mortality_rate",
    "calculate_infant_mortality_rate",
    "calculate_child_mortality_rate",
    "calculate_age_specific_death_rates",
    "calculate_direct_standardized_rate",
    "calculate_smr_and_indirect_standardized_rate",
    "calculate_whipples_index",
    "calculate_myers_blended_index",
    "calculate_pec_comparison",
    "validate_dataset_completeness",
    "run_all_quality_checks",
    "interpret_measure",
    "BENCHMARK_REGISTRY",
    "DemographicPipelineResult",
    "ComparisonResult",
    "run_demographic_pipeline",
    "compare_two_datasets",
    "load_demographic_dataset",
    "generate_sample_age_distribution_csv",
    "generate_sample_summary_csv",
]

from engine.loader import (
    load_demographic_dataset,
    generate_sample_age_distribution_csv,
    generate_sample_summary_csv,
)
