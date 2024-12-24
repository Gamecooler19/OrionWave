class AudioConfig:
    def _init_filters(self):
        self.filters = {
            'equalizer': [
                {'type': 'low_shelf', 'freq': 100, 'q': 0.7, 'gain': 0.0},
                {'type': 'peaking', 'freq': 1000, 'q': 0.7, 'gain': 0.0},
                {'type': 'high_shelf', 'freq': 10000, 'q': 0.7, 'gain': 0.0}
            ]
        }
    
    def _normalize_filter_type(self, filter_type: str) -> str:
        """Convert legacy filter types to new format"""
        type_mapping = {
            'highshelf': 'high_shelf',
            'lowshelf': 'low_shelf'
        }
        return type_mapping.get(filter_type, filter_type)
    
    def from_yaml(self, yaml_data):
        # ...existing code...
        if 'equalizer' in self.filters:
            for filter_setting in self.filters['equalizer']:
                if 'type' in filter_setting:
                    filter_setting['type'] = self._normalize_filter_type(filter_setting['type'])
        # ...existing code...
