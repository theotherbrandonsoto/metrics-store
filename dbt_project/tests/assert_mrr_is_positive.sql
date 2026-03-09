-- This test fails if any plan has zero or negative MRR
select *
from {{ ref('core_metrics') }}
where mrr <= 0