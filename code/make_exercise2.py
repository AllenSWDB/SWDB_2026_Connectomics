"""Emit code/workshops/Exercise_2.ipynb and code/solutions/Exercise_2 - Solutions.ipynb.

The two notebooks differ only in the `task(...)` cells: the student version gets the
first argument, the solutions version the second. Everything else is shared, so the
pair cannot drift apart.

Docstrings inside code cells are written with ''' because a \"\"\" would close the
r\"\"\"...\"\"\" holding the cell; build() swaps them back on the way out.
"""

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = "/Users/janne.lappalainen/Projects/SWDB/SWDB_2026_Connectomics"

C = []


def md(s):
    C.append(("markdown", s.strip("\n")))


def code(s):
    C.append(("code", s.strip("\n")))


def task(student, solution):
    C.append(("task", (student.strip("\n"), solution.strip("\n"))))


def info(body):
    md(
        '<div style="border-left: 3px solid #000; padding: 1px; padding-left: 10px; '
        'background: #F0FAFF; ">\n\n' + body.strip("\n") + "\n\n</div>"
    )


def green(body):
    md(
        '<div style="background: #DFF0D8; border-radius: 3px; padding: 10px;">\n\n'
        + body.strip("\n")
        + "\n\n</div>"
    )


# ---------------------------------------------------------------- title

TITLE = """
<img src="{logo}" width="900" style="display: block; margin: 0 auto;">

<h1 align="center">Connectomics Exercise 2: How far does like-to-like go?</h1>
{solutions_line}<h3 align="center">Summer Workshop on the Dynamic Brain 2026</h3>
"""

md("<!--TITLE-->")

info(
    """
<p>Module 2 fixed three choices to keep the logic visible: one stimulus condition
(<code>natural_images</code>), one similarity measure (Pearson correlation of the full
&Delta;F/F trace), and one cell type (L3-IT). It then reported a result: connected pairs
are more correlated than the testable pairs they are drawn from, by more than a
distance-matched null model can explain.
<p>A result that holds only for the choices you happened to make is not a result about the
brain, it is a result about your choices. This exercise relaxes them one at a time.
<ol>
<li><b>Are the seven stimulus conditions seven measurements or one?</b>
<li><b>Which condition drives the strongest correlations</b> &mdash; and is that the same as
the one that best predicts connectivity?
<li><b>Does the null-model result survive in every condition?</b> Rank them, then work out
whether the ranking is biology.
<li><b>Does any of it hold for a different cell type?</b>
</ol>
<p>The preliminaries below rebuild everything from Module 2 Parts 1&ndash;3 &mdash; there is
nothing new in them, so run them and move on. The one addition is
<code>build_pair_table</code>, which packages Parts 1&ndash;3 into a single call so that
changing cell type in Task 4 is a one-line change.
"""
)

# ---------------------------------------------------------------- preliminaries

md("## Preliminaries")

info(
    """
<p>Paths, imports and the Common Connectivity identifiers, as in Module 2.
"""
)

code(
    r"""
import sys
from os.path import join as pjoin

mat_version = 1196

# Identifiers within the Common Connectivity dataset
project_id = "v1dd"
synapse_dataset_id = f"v1dd_{mat_version}_em"
synapse_feature_matrix_id = f"v1dd_{mat_version}_synapse_features"
axon_dataset_id = f"v1dd_{mat_version}_proofread_axons"
dendrite_dataset_id = f"v1dd_{mat_version}_proofread_dendrites"

sys.path.append(pjoin("..", "utils"))

import itertools

import numpy as np
import pandas as pd
import polars as pl
import seaborn as sns
import tqdm
from connects_common_connectivity.io import DatasetReader, read_synapse_table
from matplotlib import pyplot as plt
from scipy import spatial, stats

from paths import resolve_data_root, resolve_dataset_dir
from utils import filter_synapse_table

data_root = resolve_data_root(f"v1dd_{mat_version}_ccm")

# The EM side: cells, cell types and synapses, in Common Connectivity format
ccm_dir = resolve_dataset_dir(f"v1dd_{mat_version}_ccm", root=data_root)

# The two-photon side: its own dataset on CodeOcean, but it sits next to the older feather
# tables if you downloaded those together. Accept either.
functional_dir = resolve_dataset_dir(
    f"v1dd_{mat_version}_coreg_functional_correlation",
    f"v1dd_{mat_version}",
    root=data_root,
)

print(f"ccm_dir        {ccm_dir}")
print(f"functional_dir {functional_dir}")
"""
)

info(
    """
<p>The EM side: which cells are proofread, where their somas are, what type they are, and
every synapse between them.
"""
)

code(
    r"""
reader = DatasetReader(ccm_dir)

proofread_axons = reader.read_dataset(axon_dataset_id)
proofread_dendrites = reader.read_dataset(dendrite_dataset_id)

axon_proof_root_ids = proofread_axons["dataitem_id"].cast(pl.UInt64).to_numpy()
dendrite_proof_root_ids = proofread_dendrites["dataitem_id"].cast(pl.UInt64).to_numpy()

cell_df = proofread_dendrites.select(
    pl.col("dataitem_id").cast(pl.UInt64).alias("pt_root_id"),
    # transformed coordinates, already in µm
    pl.col("soma_transformed_x").alias("pt_position_trform_x"),
    pl.col("soma_transformed_y").alias("pt_position_trform_y"),
    pl.col("soma_transformed_z").alias("pt_position_trform_z"),
    pl.col("soma_volume").alias("volume"),
    pl.col("v1dd_cell_types_level_1").alias("cell_type_coarse"),
    pl.col("v1dd_cell_types_level_2").alias("cell_type"),
).to_pandas()

synapse_data = read_synapse_table(
    project_id,
    dataset_id=synapse_dataset_id,
    features=True,
    feature_matrix_id=synapse_feature_matrix_id,
    output_root=ccm_dir,
)

syn_df = (
    synapse_data.with_columns(
        pl.col("id").cast(pl.UInt64),
        pl.col("presynaptic_cell").cast(pl.UInt64),
        pl.col("postsynaptic_cell").cast(pl.UInt64),
    )
    .rename(
        {
            "presynaptic_cell": "pre_pt_root_id",
            "postsynaptic_cell": "post_pt_root_id",
        }
    )
    .select(["id", "pre_pt_root_id", "post_pt_root_id", "size"])
    .to_pandas()
)

print(f"{len(axon_proof_root_ids):>10,} cells with proofread axons")
print(f"{len(dendrite_proof_root_ids):>10,} cells with acceptable dendrites")
print(f"{len(syn_df):>10,} synapses")
"""
)

info(
    """
<p>The two-photon side: one row per coregistered pair of cells, one column per stimulus
condition, each entry the correlation of the two &Delta;F/F traces over the frames of that
condition. Built in
<a href="../supplement/Functional%20Data%20Cell-Cell%20Correlations.ipynb">Functional Data
Cell-Cell Correlations.ipynb</a>.
"""
)

code(
    r"""
corr_coreg_df = pd.read_feather(
    f"{functional_dir}/cell_cell_correlations_by_stimulus_coregistered.feather"
)

# Everything that is not an identifier column is a stimulus condition.
# `errors="ignore"` because which metadata columns are present depends on which version
# of the table you have.
stimulus_conditions = corr_coreg_df.columns.drop(
    [
        "pre_pt_root_id",
        "post_pt_root_id",
        "column",
        "volume",
        "pre_plane",
        "pre_roi",
        "post_plane",
        "post_roi",
    ],
    errors="ignore",
)

print(f"{len(corr_coreg_df):,} coregistered pairs")
list(stimulus_conditions)
"""
)

info(
    """
<p>Two helpers from Module 2, unchanged: lateral distance between every pair of somas, and
a two-sample comparison that reports a $p$-value with an effect size beside it.
"""
)

code(
    r"""
def calculate_lateral_distances(pre_cell_df, post_cell_df=None):
    '''Calculates the lateral distances in µm between all neurons.'''
    if post_cell_df is None:
        post_cell_df = pre_cell_df

    pos_cols = ["pt_position_trform_x", "pt_position_trform_z"]
    lateral_distances = spatial.distance.cdist(
        np.array(pre_cell_df[pos_cols]), np.array(post_cell_df[pos_cols])
    )

    id_pairs = list(
        itertools.product(pre_cell_df["pt_root_id"], post_cell_df["pt_root_id"])
    )
    lateral_distance_df = pd.DataFrame(
        id_pairs, columns=["pre_pt_root_id", "post_pt_root_id"]
    )
    lateral_distance_df["distance"] = lateral_distances.flatten()

    # drop self-pairs
    return lateral_distance_df[
        lateral_distance_df["pre_pt_root_id"] != lateral_distance_df["post_pt_root_id"]
    ]


def compare_distributions(sample_a, sample_b, name_a="a", name_b="b", verbose=True):
    '''Mann-Whitney U test between two samples, with its effect size.

    Returns (p, auc), where auc is the probability that a random draw from
    `sample_a` exceeds a random draw from `sample_b`. 0.5 means no difference.
    '''
    sample_a = np.asarray(sample_a)
    sample_b = np.asarray(sample_b)
    u, p = stats.mannwhitneyu(sample_a, sample_b, alternative="two-sided")
    auc = u / (len(sample_a) * len(sample_b))

    if verbose:
        # scipy's normal approximation underflows to exactly 0.0 far enough into the
        # tail, and a p-value of 0 is not a real quantity. Report the precision limit.
        p_text = f"{p:.3g}" if p > 0 else "<1e-300"
        print(f"{name_a} (n={len(sample_a):,})  vs  {name_b} (n={len(sample_b):,})")
        print(
            f"  median      {np.median(sample_a):>10.4g}  vs {np.median(sample_b):>10.4g}"
        )
        print(f"  p           {p_text:>10}")
        print(f"  AUC         {auc:>10.3f}   (0.5 = indistinguishable)")
    return p, auc
"""
)

info(
    """
<h3> Parts 1&ndash;3 in one function </h3>
<p>Module 2 built its pair table step by step, which is the right way to see it once. Here
it is packaged, because Task 4 needs the whole thing rebuilt for a different cell type and
retyping eight cells is not the exercise.
<p><code>build_pair_table</code> returns one row per <i>testable</i> pair &mdash; presynaptic
cell has a proofread axon, postsynaptic cell has an acceptable dendrite, both are
coregistered &mdash; carrying:
<ul>
<li>every stimulus condition's activity correlation,
<li><code>distance</code>, the lateral separation of the two somas,
<li><code>connected</code>, whether a synapse was found,
<li><code>connection_probability</code>, what the measured distance-dependence of
connectivity predicts for a pair this far apart. This is the column the null model samples
with.
</ul>
<p>It is worth reading once: nothing in it is new, but Task 3 and Task 4 both depend on
knowing what is in the table.
"""
)

code(
    r"""
def build_pair_table(pre_cell_df, post_cell_df=None, max_distance=500, n_bins=100):
    '''Module 2 Parts 1-3, as one call. See the text above for the columns.

    Returns (full_df, conn_df, testable_distance_df).
    '''
    if post_cell_df is None:
        post_cell_df = pre_cell_df

    # -- Part 1: distances, restricted to pairs whose connectivity is testable
    distance_df = calculate_lateral_distances(pre_cell_df, post_cell_df)

    pre_root_ids = pre_cell_df["pt_root_id"][
        np.isin(pre_cell_df["pt_root_id"], axon_proof_root_ids)
    ]
    post_root_ids = post_cell_df["pt_root_id"][
        np.isin(post_cell_df["pt_root_id"], dendrite_proof_root_ids)
    ]
    testable_distance_df = distance_df[
        np.isin(distance_df["pre_pt_root_id"], pre_root_ids)
        & np.isin(distance_df["post_pt_root_id"], post_root_ids)
    ]

    # -- Part 1: connections, as summed synapse size per pair
    conn_df = (
        filter_synapse_table(syn_df, pre_root_ids, post_root_ids)
        .groupby(["pre_pt_root_id", "post_pt_root_id"])["size"]
        .sum()
        .reset_index()
    )
    conn_dist_df = pd.merge(
        conn_df, testable_distance_df, on=["pre_pt_root_id", "post_pt_root_id"]
    )

    # -- Part 2: the functional side, restricted the same way
    corr_testable_df = corr_coreg_df[
        np.isin(corr_coreg_df["pre_pt_root_id"], pre_root_ids)
        & np.isin(corr_coreg_df["post_pt_root_id"], post_root_ids)
    ]

    full_df = pd.merge(
        corr_testable_df, testable_distance_df, on=["pre_pt_root_id", "post_pt_root_id"]
    )
    full_df = pd.merge(
        full_df, conn_df, on=["pre_pt_root_id", "post_pt_root_id"], how="left"
    ).fillna({"size": 0})
    full_df["connected"] = full_df["size"] > 0

    # -- Part 3: connection probability per distance bin, from the measurement itself
    distance_bins = np.linspace(0, max_distance, n_bins + 1)
    probability_df = pd.DataFrame(
        {
            "bin_id": np.arange(n_bins),
            "connection_probability": (
                np.histogram(conn_dist_df["distance"], distance_bins)[0]
                / np.histogram(testable_distance_df["distance"], distance_bins)[0]
            ),
        }
    )
    full_df["bin_id"] = np.digitize(full_df["distance"], distance_bins) - 1
    full_df = pd.merge(full_df, probability_df, on="bin_id")

    return full_df, conn_df, testable_distance_df
"""
)

info(
    """
<p>Rebuilding the Module 2 analysis set: L3-IT to L3-IT. The numbers printed below should
match Module 2 Part 3 &mdash; if they do not, something above went wrong and everything
after it is suspect.
"""
)

code(
    r"""
sub_cell_df = cell_df[cell_df["cell_type"] == "L3-IT"]

full_df, conn_df, testable_distance_df = build_pair_table(sub_cell_df)

print(f"{len(sub_cell_df):>10,} L3-IT cells")
print(f"{len(testable_distance_df):>10,} testable L3-IT pairs")
print(f"{len(full_df):>10,} of those are coregistered (and within 500 µm)")
print(f"{int(full_df['connected'].sum()):>10,} of those are connected")
"""
)

# ---------------------------------------------------------------- Task 1

md("## Task 1: Are the stimulus conditions seven measurements or one?")

info(
    """
<p>Before relaxing the choice of stimulus, it is worth asking how much of a choice it was.
Two extremes:
<ul>
<li>If the correlation of a pair under drifting gratings tells you its correlation under
natural movies, the seven columns are seven noisy copies of one measurement. Module 2's
choice of <code>natural_images</code> was then arbitrary and harmless, and the seven
conditions cannot be treated as seven independent tests of anything.
<li>If they disagree, the conditions are separate measurements, the result may depend on
which one you picked, and "connected pairs are more correlated" needs the stimulus named
every time it is said.
</ul>
<p>Both are informative, and which one holds is an empirical question about this dataset.
"""
)

green(
    """
<p><b>Task 1</b> Plot the correlation <i>between the stimulus conditions</i>, across pairs:
<code>corr_coreg_df[stimulus_conditions].corr()</code> as a heatmap.
<p>Use <code>sns.heatmap</code> with <code>vmin=0</code>, <code>vmax=0.5</code>,
<code>annot=True</code>. Note what is being correlated with what: each <i>row of the
dataframe</i> is a pair of cells, each <i>column</i> a stimulus condition, so this is a
7&times;7 matrix over conditions, not over cells.
<p><b>Write down what you expect before you run it.</b> Which two conditions should agree
most? Which least?
"""
)

task(
    """
# Your code here
""",
    r"""
condition_similarity = corr_coreg_df[stimulus_conditions].corr()

fig, ax = plt.subplots(figsize=(7, 5.5), dpi=150)
sns.heatmap(
    condition_similarity,
    vmin=0,
    vmax=0.5,
    cmap="magma",
    annot=True,
    fmt=".2f",
    annot_kws={"fontsize": 8},
    square=True,
    cbar_kws={"label": "correlation across pairs"},
    ax=ax,
)
ax.set(title="Do the stimulus conditions agree about which pairs are correlated?")
plt.tight_layout()
plt.show()
""",
)

info(
    """
<p>Two things to read off the matrix. First the overall level: values well below 1 mean the
conditions are <i>not</i> interchangeable &mdash; knowing a pair's correlation under one
condition leaves most of the variance under another unexplained. Second the structure:
<code>natural_images</code> and <code>natural_images_12</code> are near-duplicate stimuli
and should agree far better with each other than with anything else, which is a useful
sanity check that the columns are what they claim to be.
<p>The practical consequence for the rest of this exercise: seven conditions is seven
tests, so a Z-score that is impressive in one condition and absent in another is a real
finding to be explained, not a rounding error. It also means that if you go hunting across
all seven for the largest effect, you are running seven tests and your $p$-values need to
know that (look up Bonferroni or Benjamini&ndash;Hochberg).
"""
)

green(
    """
<p><b>Discussion</b> The conditions differ in duration &mdash; <code>spontaneous</code> and
<code>natural_movie</code> have many more frames than <code>drifting_gratings_windowed</code>.
A correlation estimated from fewer frames is noisier. How much of the structure in this
matrix could be explained by duration alone, and how would you check?
"""
)

# ---------------------------------------------------------------- Task 2

md("## Task 2: Which condition drives the strongest correlations?")

info(
    """
<p>Task 1 established that the conditions differ. The natural next question is <i>how</i>.
There are two different things one could mean by "the strongest condition", and keeping
them apart is the point of this task:
<ol>
<li><b>Overall correlation level</b> &mdash; how correlated the population is during that
stimulus, connected or not. A stimulus that drives everything at once (a full-field
drifting grating, say) should raise all correlations together.
<li><b>How well correlation separates connected from unconnected pairs</b> &mdash; the
Module 2 result. This is a <i>difference</i> between two distributions, and a stimulus can
raise both of them equally while separating them no better at all.
</ol>
<p>These need not agree, and if they do not, then "which stimulus shows like-to-like best"
has to be answered with (2), not (1).
"""
)

green(
    """
<p><b>Task 2a</b> Overlay the correlation distributions for all seven conditions on one
axis, as in Module 2 Figure 5. Use <code>corr_coreg_df</code> (all coregistered pairs),
<code>sns.histplot</code> with <code>stat="probability"</code>,
<code>element="step"</code>, <code>fill=False</code> and shared <code>bins</code> so the
curves are comparable.
"""
)

task(
    """
# Your code here
""",
    r"""
bins = np.linspace(-0.1, 0.4, 51)

fig, ax = plt.subplots(figsize=(7.5, 4.5), dpi=150)

for condition, color in zip(stimulus_conditions, sns.color_palette("husl", 7)):
    sns.histplot(
        corr_coreg_df,
        x=condition,
        stat="probability",
        bins=bins,
        element="step",
        fill=False,
        lw=2,
        color=color,
        label=f"{condition} (mean {corr_coreg_df[condition].mean():.3f})",
        ax=ax,
    )

ax.legend(frameon=False, fontsize=8)
ax.set(
    xlabel="Total trace correlation during stimulus",
    ylabel="Fraction of neuron pairs",
    title="All coregistered pairs, one curve per condition",
)
sns.despine()
plt.show()
""",
)

green(
    """
<p><b>Task 2b</b> Now the other sense of "strongest". For each condition, compare the
connected pairs against the testable-but-not-connected pairs in <code>full_df</code>, and
collect the effect size. <code>compare_distributions(..., verbose=False)</code> returns
<code>(p, auc)</code>; the AUC is the readable one &mdash; the probability that a random
connected pair is more correlated than a random unconnected one, where 0.5 means no
separation at all.
<p>Build a dataframe with one row per condition and columns for the two means, the
difference, the AUC and $p$. Sort it by AUC. Is the order the same as the order of overall
correlation level from Task 2a?
"""
)

task(
    """
# Your code here
""",
    r"""
rows = []
for condition in stimulus_conditions:
    connected = full_df.loc[full_df["connected"], condition].dropna()
    unconnected = full_df.loc[~full_df["connected"], condition].dropna()
    p, auc = compare_distributions(connected, unconnected, verbose=False)
    rows.append(
        {
            "condition": condition,
            "mean_all": corr_coreg_df[condition].mean(),
            "mean_connected": connected.mean(),
            "mean_unconnected": unconnected.mean(),
            "difference": connected.mean() - unconnected.mean(),
            "auc": auc,
            "p": p,
        }
    )

separation_df = pd.DataFrame(rows).sort_values("auc", ascending=False)
separation_df.round(4)
""",
)

info(
    """
<p>Compare the <code>mean_all</code> column (how correlated the population is) against the
<code>auc</code> column (how well correlation separates connected pairs). If the two
orderings differ, the two senses of "strongest" really are different quantities, and any
claim of the form "like-to-like is strongest during X" must say which one it means.
<p>Watch the sample sizes too: only a few hundred pairs are both coregistered and
connected, so the AUCs come with real uncertainty. An AUC of 0.58 against 0.55 is not a
ranking you should defend without a confidence interval &mdash; bootstrap the pairs if you
want one.
"""
)

# ---------------------------------------------------------------- Task 3

md("## Task 3: Does the null-model result survive in every condition?")

info(
    """
<p>Task 2b's AUC has the weakness Module 2 Part 3 was written to address: connected pairs
are also <i>nearby</i> pairs, and nearby cells are more correlated for reasons that have
nothing to do with being wired together. Any per-condition ranking of AUCs inherits that
confound.
<p>So repeat Part 3 per condition. The null model holds the distance dependence fixed
&mdash; it samples the same number of connections, with each pair's probability taken from
the measured distance curve &mdash; and asks whether the observed mean correlation of
connected pairs is still surprising. The result is one Z-score per condition, and now
ranking them means something.
"""
)

green(
    """
<p><b>Task 3a</b> Write the sampling loop as a function. For <code>n_samples</code>
iterations: draw <code>full_df["connected"].sum()</code> pairs from
<code>full_df.index</code> with <code>np.random.choice</code>, using
<code>connection_probability</code> normalised to sum to 1 as <code>p</code>, and record
the mean of <code>condition</code> over the drawn pairs. Return the array of means.
<p>This is Module 2's Part 3 loop with the stimulus made an argument.
"""
)

task(
    """
def sample_null_means(full_df, condition, n_samples=2_000, seed=0):
    \"\"\"Mean correlation of connected pairs under `n_samples` distance-matched connectomes.\"\"\"
    # Your code here
""",
    r"""
def sample_null_means(full_df, condition, n_samples=2_000, seed=0):
    '''Mean correlation of connected pairs under `n_samples` distance-matched connectomes.'''
    rng = np.random.default_rng(seed)

    # Pairs with no correlation measured in this condition cannot enter either the
    # observed mean or the null, so drop them from both.
    usable = full_df[full_df[condition].notna()]
    probability = usable["connection_probability"]
    probability = probability / probability.sum()
    n_connected = int(usable["connected"].sum())

    values = usable[condition].to_numpy()
    means = [
        values[rng.choice(len(values), p=probability, size=n_connected)].mean()
        for _ in range(n_samples)
    ]
    return np.array(means)
""",
)

green(
    """
<p><b>Task 3b</b> Run it for every condition and collect, per condition: the observed mean
correlation of connected pairs, the null mean and standard deviation, the Z-score
$Z = (\\text{observed} - \\text{null mean}) / \\text{null sd}$, and the empirical
$p$-value
$$\\hat p = \\frac{1 + \\#\\{b : T_b \\ge t_{\\text{obs}}\\}}{1 + B}$$
Sort by Z. (2,000 samples per condition is enough for a ranking; Module 2 used 10,000 for
its single condition.)
"""
)

task(
    """
# Your code here
""",
    r"""
rows = []
for condition in tqdm.tqdm(stimulus_conditions):
    usable = full_df[full_df[condition].notna()]
    observed = usable.loc[usable["connected"], condition].mean()
    null_means = sample_null_means(full_df, condition)

    n_extreme = int((null_means >= observed).sum())
    rows.append(
        {
            "condition": condition,
            "observed": observed,
            "null_mean": null_means.mean(),
            "null_sd": null_means.std(),
            "zscore": (observed - null_means.mean()) / null_means.std(),
            "p_empirical": (1 + n_extreme) / (1 + len(null_means)),
            # kept for Task 3c: the spread Z is divided by
            "correlation_sd": usable[condition].std(),
            "n_connected": int(usable["connected"].sum()),
        }
    )

null_df = pd.DataFrame(rows).sort_values("zscore", ascending=False)
null_df.round(4)
""",
)

green(
    """
<p><b>Task 3c</b> Before reading that ranking as biology, two checks.
<ol>
<li><code>natural_images</code> and <code>natural_images_12</code> are near-duplicate
stimuli, and Task 1 showed they agree closely. If their Z-scores nevertheless disagree, the
gap between them is a <i>noise floor</i> for the whole ranking: no difference smaller than
that is interpretable.
<li>$Z$ is a difference divided by a spread. A condition can score a high $Z$ by having a
larger effect <i>or</i> by having a tighter null, and the null's width is set by the spread
of that condition's correlations and the number of connected pairs, not by biology.
</ol>
<p>Plot Z against <code>correlation_sd</code> to see how much of the ranking is spread
rather than effect. Then decide: which conditions genuinely stand apart?
"""
)

task(
    """
# Your code here
""",
    r"""
duplicates = null_df.set_index("condition").loc[
    ["natural_images", "natural_images_12"], "zscore"
]
noise_floor = abs(duplicates.diff().iloc[-1])
print(f"near-duplicate conditions differ by {noise_floor:.2f} in Z")
print("-> treat any Z difference below that as uninterpretable\n")

fig, axs = plt.subplots(1, 2, figsize=(11, 4), dpi=150)

ax = axs[0]
sns.barplot(null_df, y="condition", x="zscore", color="grey", ax=ax)
ax.axvline(0, color="k", lw=1)
ax.axvline(2, color="r", ls="--", lw=1, label="Z = 2")
ax.legend(frameon=False)
ax.set(xlabel="Z (observed vs. distance-matched null)", ylabel="")

ax = axs[1]
ax.scatter(null_df["correlation_sd"], null_df["zscore"], c="k")
for _, row in null_df.iterrows():
    ax.annotate(
        row["condition"],
        (row["correlation_sd"], row["zscore"]),
        fontsize=7,
        xytext=(4, 0),
        textcoords="offset points",
    )
ax.set(
    xlabel="SD of correlations in this condition",
    ylabel="Z",
    title="Is the ranking effect size, or spread?",
)

sns.despine()
plt.tight_layout()
plt.show()
""",
)

green(
    """
<p><b>Discussion</b> <code>spontaneous</code> is a grey screen: no visual stimulus, just
whatever the cortex does on its own. Suppose it scores as high as the visual conditions.
Is that evidence that the like-to-like result has nothing to do with vision, evidence that
spontaneous activity reflects the same wiring, or evidence of a problem with the analysis?
What further measurement would separate those?
"""
)

# ---------------------------------------------------------------- Task 4

md("## Task 4: Does any of this hold for a different cell type?")

info(
    """
<p>Everything so far is about L3-IT cells wired to other L3-IT cells &mdash; one type, in
one layer, connected to itself. That is where the statistics are best and where like-to-like
connectivity has most often been reported, which is exactly why it is a weak test of
generality.
<p>Two ways to move: another type onto itself, or one type onto a different type. The
second changes the question &mdash; for a cross-type projection there is no particular
reason to expect two cells to share a stimulus preference just because one drives the
other.
<p><code>build_pair_table</code> takes a presynaptic and a postsynaptic cell table, so both
are one line. What will bite is sample size, and the binding constraint is
<i>coregistration</i>: a pair is only usable if both cells were found in the two-photon
volume as well as the EM volume. Run the cell below before choosing a type &mdash; the
<code>coregistered</code> column is the one that decides whether a comparison is possible
at all, and it is much smaller than the cell counts beside it.
"""
)

code(
    r"""
# What is available, and how many coregistered cells each type has
coreg_ids = set(corr_coreg_df["pre_pt_root_id"]) | set(corr_coreg_df["post_pt_root_id"])

type_summary = (
    cell_df.assign(
        coregistered=cell_df["pt_root_id"].isin(coreg_ids),
        proofread_axon=cell_df["pt_root_id"].isin(axon_proof_root_ids),
    )
    .groupby(["cell_type_coarse", "cell_type"])
    .agg(cells=("pt_root_id", "size"), coregistered=("coregistered", "sum"),
         proofread_axon=("proofread_axon", "sum"))
    .sort_values("coregistered", ascending=False)
)
type_summary.head(15)
"""
)

info(
    """
<p>One more constraint, and it is the one that decides which cross-type comparisons are
even possible: the two-photon volume was imaged in separate depth ranges, and correlations
were only computed between cells recorded together. So the correlation table contains pairs
within a depth range and essentially none across. Check before you plan:
"""
)

code(
    r"""
type_of = cell_df.set_index("pt_root_id")["cell_type"]
pair_types = pd.DataFrame(
    {
        "pre": corr_coreg_df["pre_pt_root_id"].map(type_of),
        "post": corr_coreg_df["post_pt_root_id"].map(type_of),
    }
)

pair_types.groupby(["pre", "post"], dropna=True).size().sort_values(ascending=False).head(
    10
)
"""
)

green(
    """
<p><b>Task 4</b> Pick a cell type from the table above with enough coregistered cells
&mdash; there are only a few &mdash; and rerun the analysis on it. For a within-type test:
<pre><code>
other_cell_df = cell_df[cell_df["cell_type"] == "..."]
other_full_df, _, _ = build_pair_table(other_cell_df)
</code></pre>
<p>or, for a cross-type projection, pass both tables:
<code>build_pair_table(sub_cell_df, other_cell_df)</code> &mdash; picking a combination that
actually appears in the pair-type table above.
<p>Then, for <code>natural_images</code>: how many connected pairs survive? Compare
connected against unconnected with <code>compare_distributions</code>, and if the count
supports it, run <code>sample_null_means</code>. Report the number of connected pairs
alongside every result &mdash; a Z-score computed from twelve pairs is not a
finding.
"""
)

task(
    """
# Your code here
""",
    r"""
stim = "natural_images"


def rerun_analysis(pre_cell_df, post_cell_df=None, label=""):
    '''Task 2b + Task 3b for one (pre, post) cell-type combination.'''
    pair_df, _, _ = build_pair_table(pre_cell_df, post_cell_df)
    pair_df = pair_df[pair_df[stim].notna()]

    connected = pair_df.loc[pair_df["connected"], stim]
    unconnected = pair_df.loc[~pair_df["connected"], stim]
    print(f"\n{label}")
    print(f"  {len(pair_df):>6,} coregistered testable pairs")
    print(f"  {len(connected):>6,} connected")
    if len(connected) < 30:
        print("  too few connected pairs to test; reporting counts only")
        return None

    p, auc = compare_distributions(connected, unconnected, "connected", "not connected")

    null_means = sample_null_means(pair_df, stim)
    observed = connected.mean()
    zscore = (observed - null_means.mean()) / null_means.std()
    p_empirical = (1 + int((null_means >= observed).sum())) / (1 + len(null_means))
    print(f"  Z           {zscore:>10.2f}")
    print(f"  p_empirical {p_empirical:>10.4g}")
    return {"label": label, "n_connected": len(connected), "auc": auc, "z": zscore}


# Only excitatory types are coregistered in any number: L3-IT, L4-IT, L5-ET. Nothing
# inhibitory is coregistered at all, so an E -> I test is not available in this dataset,
# however interesting it would be. And of the cross-type combinations, only L3-IT <-> L4-IT
# has pairs, because L2/3-L4 and L5 were imaged separately.
l5et_cell_df = cell_df[cell_df["cell_type"] == "L5-ET"]
l4it_cell_df = cell_df[cell_df["cell_type"] == "L4-IT"]

results = [
    rerun_analysis(sub_cell_df, label="L3-IT -> L3-IT (Module 2)"),
    rerun_analysis(l5et_cell_df, label="L5-ET -> L5-ET"),
    rerun_analysis(l4it_cell_df, label="L4-IT -> L4-IT"),
    rerun_analysis(sub_cell_df, l4it_cell_df, label="L3-IT -> L4-IT"),
    rerun_analysis(l4it_cell_df, sub_cell_df, label="L4-IT -> L3-IT"),
]

pd.DataFrame([r for r in results if r is not None]).round(3)
""",
)

info(
    """
<p>Whatever you found, the honest write-up names the sample size in the same sentence as
the effect. "No effect" and "not enough pairs to detect the effect Module 2 found" are
different claims, and the way to tell them apart is a power calculation, not a $p$-value:
given the AUC measured for L3-IT, how many connected pairs would you need to detect it at
$p < 0.05$? If your new type has fewer than that, you have learned nothing about it yet.
"""
)

green(
    """
<p><b>Task 4b (bonus)</b> Two more assumptions in the null model, each a one- or two-line
change to <code>build_pair_table</code>:
<ul>
<li><b>Distance is lateral only.</b> The analysis uses tangential $(x, z)$ separation and
ignores depth, on the grounds that cells of one type sit at roughly one depth. That stops
being true the moment you cross layers &mdash; L3-IT to L5-ET pairs are separated mostly in
depth, and the null model cannot see it. Add <code>pt_position_trform_y</code> to
<code>calculate_lateral_distances</code> for a full 3D distance and rerun Task 4. Does the
cross-layer Z-score change?
<li><b>Connections are binary.</b> <code>conn_df</code> carries summed synapse size, which
the analysis then throws away with <code>size > 0</code>. Are strongly connected pairs
<i>more</i> correlated than weakly connected ones? Correlate <code>size</code> against the
activity correlation among connected pairs only &mdash; and remember that both grow with
proximity, so the distance confound is back and needs handling the same way.
</ul>
"""
)

green(
    """
<p><b>Discussion</b> The per-synapse <code>synaptictargetlabel</code> in the CCM feature
matrix (used in Exercise 1) says whether each synapse lands on a spine, a shaft or the
soma. Does the correlation effect depend on <i>where</i> the synapse lands? Sketch the
analysis, and say what the confound would be.
"""
)

# ---------------------------------------------------------------- wrap

md(
    """
## What to take away

1. **The stimulus conditions are not interchangeable** (Task 1), so a like-to-like result
   is a statement about a stimulus, not about the cortex in general.
2. **"Strongest" is ambiguous** (Task 2). The condition with the highest correlations
   overall need not be the one where correlation best predicts connectivity, and those two
   readings support different claims.
3. **Ranking requires the null model** (Task 3), and even then, part of the ranking is the
   width of the null rather than the size of the effect. Two near-duplicate stimuli set the
   noise floor for free — use them.
4. **Generality is a sample-size question first** (Task 4). Outside L3-IT the counts fall
   fast — a few hundred connected pairs becomes a few dozen — and "no effect" usually means
   "no power". The dataset also decides which questions are askable at all: no inhibitory
   cell is coregistered, and the imaging depth ranges mean cross-layer pairs mostly do not
   exist.

None of that weakens the Module 2 result. It locates it: L3-IT to L3-IT, during natural
images, at a strength that a distance-matched null cannot produce. Every word in that
sentence was earned by one of the tasks above.
"""
)


# ---------------------------------------------------------------- emit

def build(solutions):
    cells = []
    for kind, payload in C:
        if kind == "task":
            t, src = "code", payload[1] if solutions else payload[0]
        else:
            t, src = kind, payload
        if t == "code":
            # Docstrings above use ''' because a """ would close the r"""...""" holding
            # the cell. Emit the idiomatic quoting in the notebook.
            src = src.replace("'''", '"""')
        cells.append(
            {
                "cell_type": t,
                "metadata": {},
                "source": src.splitlines(keepends=True),
                **({"outputs": [], "execution_count": None} if t == "code" else {}),
            }
        )

    title = TITLE.format(
        logo="../workshops/img/swdb_logo.jpg" if solutions else "img/swdb_logo.jpg",
        solutions_line='<h2 align="center">SOLUTIONS</h2>\n' if solutions else "",
    ).strip("\n")
    cells[0]["source"] = title.splitlines(keepends=True)

    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3 (ipykernel)",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3.11"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


for solutions, path in [
    (False, os.path.join(REPO, "code", "workshops", "Exercise_2.ipynb")),
    (True, os.path.join(REPO, "code", "solutions", "Exercise_2 - Solutions.ipynb")),
]:
    with open(path, "w") as f:
        json.dump(build(solutions), f, indent=1)
        f.write("\n")
    print(f"wrote {path}")
