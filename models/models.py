import torch
import sys
import os
from pathlib import Path

from catt.ed_pl import TashkeelModel as EDModel
from catt.eo_pl import TashkeelModel as EOModel
from catt.tashkeel_tokenizer import TashkeelTokenizer
from catt.utils import remove_non_arabic


class TashkeelModelWrapper:
    """Wrapper for Tashkeel models to provide a consistent interface for both ED and EO models."""

    def __init__(self, model_type="ed", device=None):
        """
        Initialize the model wrapper

        Args:
            model_type: 'ed' or 'eo', defaults to 'ed'
            device: 'cuda' or 'cpu', defaults to what's available on the system
        """
        self.model_type = model_type
        self.tokenizer = TashkeelTokenizer()

        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        if model_type == "ed":
            ckpt_path = Path("catt/models/best_ed_mlm_ns_epoch_178.pt")
            # convert this to path object
            self.max_seq_len = 1024
            self.model = EDModel(
                self.tokenizer,
                max_seq_len=self.max_seq_len,
                n_layers=3,
                learnable_pos_emb=False,
            )
        elif model_type == "eo":
            ckpt_path = Path("catt/models/best_eo_mlm_ns_epoch_193.pt")

            self.max_seq_len = 1024
            self.model = EOModel(
                self.tokenizer,
                max_seq_len=self.max_seq_len,
                n_layers=6,
                learnable_pos_emb=False,
            )
        else:
            raise ValueError(f"Invalid model_type: {model_type}. Must be 'ed' or 'eo'")

        # Check if model file exists
        if not ckpt_path.exists():
            raise FileNotFoundError(f"Model file not found at {ckpt_path}")

        # Load model weights
        self.model.load_state_dict(torch.load(ckpt_path, map_location=self.device))
        self.model.eval().to(self.device)

    def tashkeel(self, text, clean_text=True, batch_size=16, verbose=False):
        """
        Apply diacritics (tashkeel) to the given text

        Args:
            text: Input text without diacritics
            clean_text: Whether to clean non-Arabic characters, defaults to True
            batch_size: Batch size for inference, defaults to 16
            verbose: Whether to show progress, defaults to False

        Returns:
            Text with diacritics (tashkeel)
        """
        if isinstance(text, str):
            texts = [text]
        else:
            texts = text

        # Clean text if needed
        if clean_text:
            texts = [remove_non_arabic(t) for t in texts]

        # Run inference
        results = self.model.do_tashkeel_batch(
            texts, batch_size=batch_size, verbose=verbose
        )

        # Return single string if input was a string
        if isinstance(text, str):
            return results[0]

        return results


# Singleton instances to avoid loading models multiple times
_ed_model = None
_eo_model = None


def get_model(model_type="ed", device=None):
    """
    Get a model instance, reusing existing instances when possible.

    Args:
        model_type: 'ed' or 'eo', defaults to 'ed'
        device: 'cuda' or 'cpu', defaults to what's available

    Returns:
        TashkeelModelWrapper instance
    """
    global _ed_model, _eo_model

    if model_type == "ed":
        if _ed_model is None:
            _ed_model = TashkeelModelWrapper(model_type="ed", device=device)
        return _ed_model
    elif model_type == "eo":
        if _eo_model is None:
            _eo_model = TashkeelModelWrapper(model_type="eo", device=device)
        return _eo_model
    else:
        raise ValueError(f"Invalid model_type: {model_type}. Must be 'ed' or 'eo'")
