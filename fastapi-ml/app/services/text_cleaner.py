"""
Text cleaning and preprocessing service for improved RAG performance.
Supports both English and Indonesian languages simultaneously.
"""
import re
from typing import List, Set, Dict, Any
import spacy
from loguru import logger


class TextCleaner:
    """Text cleaning service for document processing and query preprocessing."""
    
    def __init__(self):
        """Initialize the text cleaner with multi-language support."""
        self.nlp_models: Dict[str, Any] = {}
        self._stop_words: Dict[str, Set[str]] = {}
        self._initialize_multilingual_support()
        
        # Text cleaning patterns (support international phone numbers)
        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'(\+?[\d\-.\s]?)?\(?([0-9]{2,4})\)?[-.\s]?([0-9]{3,4})[-.\s]?([0-9]{4,6})')
        self.extra_whitespace_pattern = re.compile(r'\s+')
        self.non_alpha_pattern = re.compile(r'[^a-zA-Z0-9\s]')
        
        # Minimum word length for keeping words
        self.min_word_length = 2
        
        logger.info("Initialized TextCleaner with multi-language support (English + Indonesian)")
    
    def _initialize_multilingual_support(self):
        """Initialize spaCy models for both English and Indonesian."""
        # Language configurations
        self.language_configs = {
            "en": {
                "model": "en_core_web_sm",
                "fallback_model": None,
                "custom_stop_words": {
                    'page', 'document', 'file', 'pdf', 'docx', 'txt', 'csv',
                    'figure', 'table', 'image', 'chart', 'section', 'chapter',
                    'appendix', 'reference', 'bibliography', 'footnote',
                    'copyright', 'reserved', 'rights', 'inc', 'ltd', 'corp'
                }
            },
            "id": {  # Indonesian
                "model": None,  # No specific Indonesian model available
                "fallback_model": "xx_ent_wiki_sm",  # Multi-language model
                "custom_stop_words": {
                    # Indonesian stop words
                    'dan', 'di', 'ke', 'dari', 'dalam', 'untuk', 'pada', 'dengan', 'yang', 'adalah',
                    'ini', 'itu', 'akan', 'telah', 'sudah', 'dapat', 'bisa', 'juga', 'atau', 'tetapi',
                    'karena', 'sebab', 'oleh', 'saya', 'anda', 'dia', 'mereka', 'kita', 'kami',
                    'ada', 'tidak', 'belum', 'masih', 'hanya', 'setiap', 'semua', 'beberapa',
                    'satu', 'dua', 'tiga', 'empat', 'lima', 'enam', 'tujuh', 'delapan', 'sembilan', 'sepuluh',
                    # Document-specific Indonesian terms
                    'halaman', 'dokumen', 'berkas', 'gambar', 'tabel', 'bab', 'bagian', 'lampiran',
                    'referensi', 'daftar', 'pustaka', 'catatan', 'kaki', 'hak', 'cipta', 'pt', 'cv', 'tbk',
                    'bab', 'pasal', 'ayat', 'huruf', 'angka', 'nomor', 'tanggal', 'bulan', 'tahun'
                }
            }
        }
        
        # Initialize models for both languages
        for lang_code in ["en", "id"]:
            self._initialize_language_model(lang_code)
    
    def _initialize_language_model(self, lang_code: str):
        """Initialize spaCy model for a specific language."""
        if lang_code not in self.language_configs:
            logger.warning(f"Language {lang_code} not supported")
            return
        
        config = self.language_configs[lang_code]
        nlp = None
        
        # Try to load the specific model first
        if config["model"]:
            try:
                nlp = spacy.load(config["model"])
                logger.info(f"Loaded spaCy model '{config['model']}' for {lang_code}")
            except OSError:
                logger.warning(f"Failed to load spaCy model '{config['model']}' for {lang_code}")
        
        # Try fallback model if primary model failed
        if nlp is None and config["fallback_model"]:
            try:
                nlp = spacy.load(config["fallback_model"])
                logger.info(f"Loaded fallback spaCy model '{config['fallback_model']}' for {lang_code}")
            except OSError:
                logger.warning(f"Failed to load fallback model '{config['fallback_model']}' for {lang_code}")
        
        # Create blank model if no models available
        if nlp is None:
            try:
                nlp = spacy.blank(lang_code)
                logger.info(f"Created blank spaCy model for {lang_code}")
            except Exception as e:
                logger.error(f"Failed to create blank model for {lang_code}: {e}")
                nlp = None
        
        # Store the model and initialize stop words
        self.nlp_models[lang_code] = nlp
        
        if nlp is not None:
            # Get stop words from spaCy if available
            stop_words = set()
            if hasattr(nlp, 'Defaults') and hasattr(nlp.Defaults, 'stop_words'):
                stop_words = nlp.Defaults.stop_words.copy()
            
            # Add custom stop words
            stop_words.update(config["custom_stop_words"])
            self._stop_words[lang_code] = stop_words
            
            logger.info(f"Initialized {len(stop_words)} stop words for {lang_code}")
        else:
            # Fallback to custom stop words only
            self._stop_words[lang_code] = config["custom_stop_words"]
            logger.warning(f"Using custom stop words only for {lang_code} (no NLP model available)")
    
    def _detect_language(self, text: str) -> str:
        """
        Detect the primary language of the text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Language code ('en' or 'id')
        """
        if not text or len(text.strip()) < 10:
            return "en"  # Default to English for short texts
        
        # Simple heuristic-based language detection
        text_lower = text.lower()
        
        # Indonesian language indicators
        indonesian_indicators = [
            'dan', 'atau', 'yang', 'adalah', 'dalam', 'untuk', 'pada', 'dengan',
            'dari', 'ke', 'di', 'akan', 'telah', 'sudah', 'dapat', 'bisa',
            'ini', 'itu', 'saya', 'anda', 'dia', 'mereka', 'kita', 'kami',
            'tidak', 'belum', 'juga', 'karena', 'sebab', 'oleh', 'ada'
        ]
        
        # English language indicators
        english_indicators = [
            'and', 'or', 'the', 'is', 'are', 'in', 'for', 'on', 'with',
            'from', 'to', 'at', 'will', 'have', 'has', 'can', 'could',
            'this', 'that', 'you', 'they', 'we', 'us', 'them',
            'not', 'also', 'because', 'by', 'there'
        ]
        
        # Count indicators
        indonesian_count = sum(1 for word in indonesian_indicators if f' {word} ' in f' {text_lower} ')
        english_count = sum(1 for word in english_indicators if f' {word} ' in f' {text_lower} ')
        
        # Determine language based on indicator counts
        if indonesian_count > english_count:
            return "id"
        else:
            return "en"
    
    def _process_multilingual_text(self, text: str, aggressive_cleaning: bool = False) -> str:
        """
        Process text using both English and Indonesian models and combine results.
        
        Args:
            text: Input text to process
            aggressive_cleaning: Whether to apply aggressive cleaning
            
        Returns:
            Processed text combining both language models
        """
        if not text:
            return text
        
        # Detect primary language
        primary_lang = self._detect_language(text)
        secondary_lang = "id" if primary_lang == "en" else "en"
        
        logger.debug(f"Detected primary language: {primary_lang}")
        
        # Process with primary language model first
        primary_result = self._process_with_spacy(text, remove_stop_words=aggressive_cleaning, language=primary_lang)
        
        # If primary result is significantly shorter, also try secondary language
        if len(primary_result.split()) < len(text.split()) * 0.5:
            logger.debug(f"Primary result too short, trying secondary language: {secondary_lang}")
            secondary_result = self._process_with_spacy(text, remove_stop_words=aggressive_cleaning, language=secondary_lang)
            
            # Use the result with more content
            if len(secondary_result.split()) > len(primary_result.split()):
                logger.debug("Using secondary language result")
                return secondary_result
        
        return primary_result
    
    def clean_document_text(self, text: str, aggressive: bool = False) -> str:
        """
        Clean document text for better storage and retrieval.
        
        Args:
            text: Raw text to clean
            aggressive: If True, apply more aggressive cleaning
            
        Returns:
            Cleaned text
        """
        if not text or not text.strip():
            return ""
        
        try:
            logger.debug(f"Cleaning document text of length {len(text)}")
            
            # Step 1: Basic normalization
            text = self._normalize_text(text)
            
            # # Step 2: Remove unwanted patterns
            # text = self._remove_patterns(text, aggressive=aggressive)
            
            # # Step 3: Process with multilingual spaCy models
            # text = self._process_multilingual_text(text, aggressive_cleaning=aggressive)
            
            # # Step 4: Final cleanup
            # text = self._final_cleanup(text)
            
            logger.debug(f"Cleaned text length: {len(text)}")
            return text
            
        except Exception as e:
            logger.error(f"Error cleaning document text: {e}")
            # Return original text if cleaning fails
            return text.strip()
    
    def clean_query_text(self, query: str) -> str:
        """
        Clean query text for better retrieval matching.
        
        Args:
            query: Raw query text
            
        Returns:
            Cleaned query text
        """
        if not query or not query.strip():
            return ""
        
        try:
            logger.debug(f"Cleaning query: '{query[:100]}...'")
            
            # Step 1: Basic normalization (less aggressive for queries)
            # text = self._normalize_text(query)
            text = query
            
            # Step 2: Remove patterns but keep more context for queries
            text = self._remove_patterns(text, aggressive=False)
            
            # Step 3: Process with multilingual models (keep stop words for better context)
            # text = self._process_multilingual_text(text, aggressive_cleaning=False)
            
            # Step 4: Final cleanup
            # text = self._final_cleanup(text)
            
            logger.debug(f"Cleaned query: '{text}'")
            return text
            
        except Exception as e:
            logger.error(f"Error cleaning query text: {e}")
            # Return original query if cleaning fails
            return query.strip()
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text with basic preprocessing."""
        # Convert to lowercase
        text = text.lower()
        
        # # Normalize unicode characters
        # text = text.encode('ascii', 'ignore').decode('ascii')
        
        # # Replace multiple whitespace with single space
        text = self.extra_whitespace_pattern.sub(' ', text)
        
        return text.strip()
    
    def _remove_patterns(self, text: str, aggressive: bool = False) -> str:
        """Remove unwanted patterns from text."""
        # Remove URLs
        # text = self.url_pattern.sub(' ', text)
        
        # Remove email addresses
        # text = self.email_pattern.sub(' ', text)
        
        # Remove phone numbers
        # text = self.phone_pattern.sub(' ', text)
        
        if aggressive:
            # Remove all punctuation and special characters
            text = self.non_alpha_pattern.sub(' ', text)
        else:
            # Keep some punctuation that might be meaningful
            # Remove excessive punctuation but keep basic ones
            text = re.sub(r'[^\w\s\.\,\!\?\-]', ' ', text)
            text = re.sub(r'[\.]{2,}', '.', text)  # Multiple dots to single
            text = re.sub(r'[!]{2,}', '!', text)   # Multiple exclamations
            text = re.sub(r'[\?]{2,}', '?', text)  # Multiple questions
        
        # Clean up whitespace again
        text = self.extra_whitespace_pattern.sub(' ', text)
        
        return text.strip()
    
    def _process_with_spacy(self, text: str, remove_stop_words: bool = True, language: str = "en") -> str:
        """Process text with spaCy for lemmatization and linguistic analysis."""
        if not text:
            return text
        
        # Get the appropriate NLP model for the language
        nlp = self.nlp_models.get(language)
        stop_words = self._stop_words.get(language, set())
        
        if not nlp:
            logger.warning(f"No NLP model available for language: {language}")
            return text
        
        try:
            # Process text with spaCy
            doc = nlp(text)
            
            # Extract lemmatized tokens
            processed_tokens = []
            
            for token in doc:
                # Skip tokens that are too short
                if len(token.text) < self.min_word_length:
                    continue
                
                # Skip stop words if requested (check both spaCy's is_stop and our custom list)
                if remove_stop_words:
                    if hasattr(token, 'is_stop') and token.is_stop:
                        continue
                    if token.text.lower() in stop_words:
                        continue
                
                # Skip punctuation and spaces
                if token.is_punct or token.is_space:
                    continue
                
                # Skip tokens that are mostly numbers (but keep alphanumeric)
                if token.like_num and not any(c.isalpha() for c in token.text):
                    continue
                
                # Use lemma if available and meaningful, otherwise use original token
                lemma = None
                if hasattr(token, 'lemma_') and token.lemma_:
                    lemma = token.lemma_.strip()
                    # Don't use placeholder lemmas
                    if lemma in ['-PRON-', 'PRON']:
                        lemma = None
                
                if lemma and lemma != token.text.lower():
                    processed_tokens.append(lemma.lower())
                elif token.text.strip():
                    processed_tokens.append(token.text.lower())
            
            return ' '.join(processed_tokens)
            
        except Exception as e:
            logger.warning(f"spaCy processing failed for language {language}: {e}")
            return text
    
    def _final_cleanup(self, text: str) -> str:
        """Final cleanup of processed text."""
        # Remove extra whitespace
        text = self.extra_whitespace_pattern.sub(' ', text)
        
        # Remove very short words (single characters except 'a' and 'i')
        words = text.split()
        filtered_words = []
        
        for word in words:
            if len(word) >= self.min_word_length or word in {'a', 'i'}:
                filtered_words.append(word)
        
        text = ' '.join(filtered_words)
        
        return text.strip()
    
    def extract_key_terms(self, text: str, max_terms: int = 10) -> List[str]:
        """
        Extract key terms from text using spaCy's linguistic features for both languages.
        
        Args:
            text: Input text
            max_terms: Maximum number of terms to return
            
        Returns:
            List of key terms
        """
        if not text:
            return []
        
        # Detect primary language
        primary_lang = self._detect_language(text)
        nlp = self.nlp_models.get(primary_lang)
        
        if not nlp:
            logger.warning(f"No NLP model available for key term extraction in language: {primary_lang}")
            return []
        
        try:
            doc = nlp(text)
            
            # Collect important terms
            key_terms = set()
            
            # Add named entities if available
            if hasattr(doc, 'ents'):
                for ent in doc.ents:
                    if len(ent.text) > 2 and not ent.text.isdigit():
                        key_terms.add(ent.text.lower())
            
            # Add noun phrases if available
            if hasattr(doc, 'noun_chunks'):
                for chunk in doc.noun_chunks:
                    if len(chunk.text) > 2 and len(chunk.text.split()) <= 3:
                        key_terms.add(chunk.text.lower())
            
            # Add important individual tokens
            for token in doc:
                # Check if POS tagging is available
                pos_tag = getattr(token, 'pos_', None)
                if pos_tag and pos_tag in {'NOUN', 'PROPN', 'ADJ'}:
                    if (not getattr(token, 'is_stop', False) and 
                        not getattr(token, 'is_punct', True) and 
                        len(token.text) > 2):
                        lemma = getattr(token, 'lemma_', token.text)
                        key_terms.add(lemma.lower())
                elif len(token.text) > 2 and token.text.isalpha():
                    # Fallback for models without POS tagging
                    stop_words = self._stop_words.get(primary_lang, set())
                    if token.text.lower() not in stop_words:
                        key_terms.add(token.text.lower())
            
            # Sort by length (longer terms first) and limit
            sorted_terms = sorted(key_terms, key=len, reverse=True)
            return sorted_terms[:max_terms]
            
        except Exception as e:
            logger.warning(f"Key term extraction failed for language {primary_lang}: {e}")
            return []
    
    def get_cleaning_stats(self, original_text: str, cleaned_text: str) -> dict:
        """Get statistics about the cleaning process."""
        # Detect language of original text
        detected_lang = self._detect_language(original_text) if original_text else "en"
        
        return {
            "original_length": len(original_text),
            "cleaned_length": len(cleaned_text),
            "reduction_ratio": 1 - (len(cleaned_text) / len(original_text)) if original_text else 0,
            "original_words": len(original_text.split()) if original_text else 0,
            "cleaned_words": len(cleaned_text.split()) if cleaned_text else 0,
            "detected_language": detected_lang,
            "available_languages": list(self.nlp_models.keys()),
            "nlp_models_loaded": {lang: model is not None for lang, model in self.nlp_models.items()}
        }


# Global text cleaner instance
text_cleaner = TextCleaner()
