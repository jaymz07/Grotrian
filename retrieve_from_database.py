import yaml
import pandas as pd

from grotrian import Grotrian
from ASDCache import SpectraCache

def ASD_to_yaml(atomic_species, output_file='temp.yaml', N_levels=20, show_fine_structure=False, labels=True):
    """
    Retrieve atomic energy levels from NIST ASD and export them as a
    Grotrian-compatible YAML file.

    Energy levels are retrieved using ASDCache and grouped by electronic
    configuration and spectroscopic term. Terms containing multiple
    fine-structure components are represented by a parent level whose
    energy is the mean of the component energies. Individual J levels
    can optionally be included as nested sublevels.

    Parameters
    ----------
    atomic_species : str
        Atomic species identifier understood by NIST ASD, such as
        ``'Rb I'``, ``'Rb II'``, or ``'Ca II'``.

    output_file : str, optional
        Destination path for the generated YAML file.
        Defaults to ``'temp.yaml'``.

    N_levels : int, optional
        Maximum number of NIST energy-level records to consider, taken
        from the beginning of the returned dataset. Defaults to 20.

    show_fine_structure : bool, optional
        If True, include individual fine-structure J components as
        nested sublevels. If False, represent each configuration/term
        group by a single parent level. Defaults to False.

    labels : bool, optional
        If True, include configuration labels in the generated diagram.
        If False, omit these labels. Defaults to True.

    Returns
    -------
    None
        Writes the generated YAML representation to ``output_file``.

    Notes
    -----
    The generated YAML is intended to be loaded directly by the
    ``Grotrian`` class. NIST ASD does not generally provide hyperfine
    structure or isotope-specific level information in the form needed
    for detailed diagrams; these can be added manually to the exported
    YAML file.

    Fine-structure energy offsets are calculated relative to the mean
    energy of their corresponding term.
    """
    nist = SpectraCache()
    levels = nist.levels.fetch(atomic_species)

    data = _parse_ASD_data( levels,
                show_fine_structure=show_fine_structure,
                labels=labels,
                N=N_levels )

    with open(output_file, "w", encoding="utf-8") as yaml_file:
        yaml.dump(
            data,
            yaml_file,
            default_flow_style=False,  # Forces block style (clean indentation)
            sort_keys=False            # Keeps the exact dictionary order from Python
        )

def _parse_ASD_data(levels, N=30, show_fine_structure=True, labels=True, label_fine_structure=False):
    """
    Convert NIST ASD energy-level data into a Grotrian-compatible dictionary
    which is ready for YAML serialization.

    Levels are grouped by electronic configuration and spectroscopic term.
    Fine-structure components are optionally represented as nested sublevels.

    Parameters
    ----------
    levels : pandas.DataFrame
        Energy-level data retrieved from NIST ASD.
    N : int, optional
        Maximum number of records to process. Defaults to 30.
    show_fine_structure : bool, optional
        Include individual J components as nested sublevels.
    labels : bool, optional
        Include configuration labels for the levels.
    label_fine_structure : bool, optional
        Include J-value labels for fine-structure sublevels.

    Returns
    -------
    dict
        Dictionary containing the Grotrian diagram data, ready for YAML
        serialization.
    """
    data = {'format': 'grotrian',
            'version': 1,
            'diagram': {
                'title': "Auto-generated YAML",
                'vertical_axis': {'property': 'Energy (cm-1)', 'unit': 'cm-1'},
                'horizontal_axis': {'order': []} # Filled later!
            }}

    out_levels = []
    cols = []
    groups = {}

    for i, level in levels.head(N).iterrows():
        J, g, L = level['J'], level['g'], level['L']
        config, term = level['Configuration'], level['Term']
        if pd.isna(J) or pd.isna(term) or pd.isna(config):
            continue
        energ = level['Level (cm-1)']

        col = term

        group_id = f"{config}_{term}"
        if group_id not in groups:
            groups[group_id] = [level]
        else:
            groups[group_id].append(level)

        if col not in cols:
            cols.append(col)

    data['diagram']['horizontal_axis']['order'] = cols

    for g_id, group in groups.items():
        level=group[0]
        if len(group) == 1:
            J, g, L = level['J'], level['g'], level['L']
            config, term = level['Configuration'], level['Term']
            energ = level['Level (cm-1)']

            col = term
            lvl_id = f"{config}_{term}_{J}"
            lbl = ""
            if labels:
                lbl = f"{config}"

            out_level = {'id': lvl_id,
                         'label': lbl,
                         'col': col,
                         'energy': energ }
        else:
            g, L = level['g'], level['L']
            config, term = level['Configuration'], level['Term']

            e_mean = []
            for l in group:
                e_mean.append(l['Level (cm-1)'])
            energ = sum(e_mean)/len(e_mean)

            col = term
            lvl_id = f"{config}_{term}"
            lbl = ""
            if labels:
                lbl = f"{config}"

            out_level = {'id': lvl_id,
                         'label': lbl,
                         'col': col,
                         'energy': energ }

            split_levels = []
            for l in group:
                J = l['J']
                split_id = f"{config}_{term}_{J}"
                split_lbl = ""
                if label_fine_structure:
                    split_lbl = f"$j={int(J*2)}/2$"
                split_level = {'id': split_id,
                             'label': split_lbl,
                             'offset': l['Level (cm-1)'] - energ,
                             'loc': 'right' }
                split_levels.append(split_level)

            if show_fine_structure:
                out_level['split'] = split_levels

        out_levels.append(out_level)

    data['levels'] = out_levels

    return data
