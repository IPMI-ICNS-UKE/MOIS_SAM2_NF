#!/bin/bash
export CUDA_VISIBLE_DEVICES=0
export PYTHONPATH=$(dirname "$(dirname "$(pwd)")"):$PYTHONPATH
export PYTHONPATH="/home/gkolokolnikov/PhD_project/nf_segmentation_interactive/NFInteractiveSegmentationBenchmarkingPrivate/model_code/VISTA_Neurofibroma/vista3d:$PYTHONPATH"

FOLDS=(1 2 3)
NETWORK="MOIS_SAM2"
NETWORK_POSFIX="sam_automatic"
EVAL_MODE="lesion_wise_corrective"
MOIS_SAM2_LESION_VS_SCAN_VALIDATION=$EVAL_MODE


USE_COM_DECODER=false
INFERENCE_ALL_SLICES=true
NUM_INTERACTIONS_PER_LESION=3
NUM_LESIONS=20
NUMBER_OF_EXEMPLARS=8
USE_ONLY_PROMPTED_EXEMPLARS=false
FILTER_EXEMPLAR_PREDICTION=true
MIN_LESION_AREA=10
NO_PROP_BEYOND_LESIONS=true

CACHE_DIR="/home/gkolokolnikov/PhD_project/nf_segmentation_interactive/NFInteractiveSegmentationBenchmarkingPrivate/evaluation/cache_0"

echo "Running $NETWORK with evaluation mode: $EVAL_MODE"

for FOLD in "${FOLDS[@]}"; do
    echo "Processing test set $FOLD..."
    python ../pipelines/evaluation_pipeline.py \
            --cache_dir $CACHE_DIR \
            --network_type $NETWORK \
            --force_network_postfix $NETWORK_POSFIX \
            --no_prop_beyond_lesions $NO_PROP_BEYOND_LESIONS \
            --exemplar_use_com $USE_COM_DECODER \
            --min_lesion_area_threshold $MIN_LESION_AREA \
            --filter_prev_prediction_components $FILTER_EXEMPLAR_PREDICTION \
            --exemplar_use_only_prompted $USE_ONLY_PROMPTED_EXEMPLARS \
            --exemplar_inference_all_slices $INFERENCE_ALL_SLICES \
            --exemplar_num $NUMBER_OF_EXEMPLARS \
            --fold $FOLD \
            --evaluation_mode $EVAL_MODE \
            --num_lesions $NUM_LESIONS \
            --num_interactions_per_lesion $NUM_INTERACTIONS_PER_LESION \
            --test_set_id $FOLD \
            --save_predictions \
            --use_gpu \
            --lesion_vs_scan_validation $MOIS_SAM2_LESION_VS_SCAN_VALIDATION
done

echo "Completed $NETWORK with $EVAL_MODE"
