def load_explainers():
    try:
        from explainer_copy import EXPLAINERS, EXPLAINERS_P2, EXPLAINERS_P3, EXPLAINERS_P4
        return EXPLAINERS, EXPLAINERS_P2, EXPLAINERS_P3, EXPLAINERS_P4
    except ModuleNotFoundError:
        return {}, {}, {}, {}
