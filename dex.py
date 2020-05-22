import sqlite3, os
    

class Dex(object):
    def __init__(self, name='Unknown Dex'):
        self.name = name
        self.versions = []
        self.languages = []
        self.current_index = 1
        
    def get_list(self, index_from=None, index_to=None):
        if index_from is None: index_from = 0
        if index_to is None: index_to = len(self)
        names = []
        for i in range(index_from, index_to):
            names.append(self.get_data_of(i)['name'])
        return names
    
    def set_current_entry(self, entry):
        self.current_index = entry
    def next_entry(self):
        self.current_index = (self.current_index+1)%len(self)
    def prev_entry(self):
        self.current_index = (self.current_index-1)%len(self)
    
    def get_current_entry(self):
        return self.get_data_of(self.current_index)
    
    def get_image_files(self):
        raise NotImplementedError()
        
    def get_sound_files(self):
        raise NotImplementedError()
        
    def change_language(self, language):
        raise NotImplementedError()
            
    def change_version(self, version):
        raise NotImplementedError()
        
    def get_sprite_of(self, index):
        raise NotImplementedError()
    def get_sound_of(self, index):
        raise NotImplementedError()
    def get_data_of(self, index):
        raise NotImplementedError()
        
    def __len__(self):
        raise NotImplementedError()
    
    
    
class VeekunPokedex(Dex):
    
    def __init__(self, version='Black', language='English', load_info=True):
        super().__init__('PokeDex')
        self.conn = sqlite3.connect('pokedex.sqlite')
        #GET VERSIONS
        query = """SELECT versions.id, version_names.name
        FROM versions 
        INNER JOIN version_names ON version_names.version_id=versions.id 
        WHERE version_names.local_language_id=9
        """
        cursor = self.conn.execute(query)
        self.versions = []
        self.version_ids = {}
        for index,ver in cursor.fetchall():
            self.versions.append(ver)
            self.version_ids[ver] = index
        #GET LANGUAGES
        query = """SELECT id, language_names.name 
        FROM languages 
        INNER JOIN language_names ON language_names.language_id=languages.id 
        WHERE language_names.local_language_id=9
        """
        cursor = self.conn.execute(query)
        self.languages = []
        self.lang_ids = {}
        for index,lang in cursor.fetchall():
            self.languages.append(lang)
            self.lang_ids[lang] = index
           
        self.version = version
        self.language = language
        self._cache_info = False #so that len(self) works
        self._cache_info = self._query_info(0, len(self)) if load_info else False
        
        self.img_files = []
        self.cry_files = []
        for i in range(len(self)):
            self.img_files.append('pokemon/global-link/%s.png' % (i+1))
            self.cry_files.append('pokemon/cries/%s.ogg' % (i+1))
            
                
    def get_image_files(self):
        return self.img_files
        
    def get_sound_files(self):
        return self.cry_files
        
    def change_language(self, language):
        self.language = language
        if self._cache_info:
            self._cache_info = self._query_info(0, len(self))
            
    def change_version(self, version):
        self.version = version
        if self._cache_info:
            self._cache_info = self._query_info(0, len(self))
    
    def _query_info(self, index, index_to=None):
        if index_to is None:
            single_value = True
            index_to = index+1
        else: single_value = False
            
        pkmn_id = index+1
        pkmn_id_to = index_to
            
        query = """ SELECT psn.name, tn1.name, tn2.name, psft.flavor_text FROM pokemon p
        INNER JOIN pokemon_species_names psn 
            ON psn.pokemon_species_id=p.id AND psn.local_language_id={2}
        INNER JOIN pokemon_species_flavor_text psft 
            ON psft.species_id=p.id AND psft.language_id={2} AND psft.version_id={3}
        INNER JOIN pokemon_types pt1 
            ON pt1.pokemon_id=p.id AND pt1.slot=1
        INNER JOIN type_names tn1 
            ON pt1.type_id=tn1.type_id AND tn1.local_language_id={2}
        LEFT JOIN pokemon_types pt2 
            ON pt2.pokemon_id=p.id AND pt2.slot=2
        LEFT JOIN type_names tn2 
            ON tn2.type_id=pt2.type_id AND tn2.local_language_id={2}
        WHERE p.id>={0} AND p.id<={1} AND p.id=p.species_id
        """.format(pkmn_id, pkmn_id_to, self.lang_ids[self.language], self.version_ids[self.version])
        cursor = self.conn.execute(query)
        infos = []
        for pkmn in cursor.fetchall():
            infos.append({
                'name': pkmn[0],
                'description': pkmn[3],
                'type1': pkmn[1],
                'type2': pkmn[2],
            })
        if single_value: return infos[0]
        else: return infos
            
    
    def _get_info(self, index):
        if self._cache_info:
            return self._cache_info[index]
        return self._query_info(index)
                
    def get_sprite_of(self, index):
        return self.img_files[index]
                
    def get_sound_of(self, index):
        return self.cry_files[index]
        
        
    def get_data_of(self, index):
        info = self._get_info(index)
        sprite = self.get_sprite_of(index)
        cry = self.get_sound_of(index)
        
        data = {}
        data['id'] = index+1
        data['name'] = info['name']
        data['description'] = info['description']
        data['type1'] = info['type1']
        data['type2'] = info['type2']
        data['image'] = sprite
        data['sound'] = cry
        return data
    
    
    
    def __len__(self):
        if self._cache_info:
            return len(self._cache_info)
        cursor = self.conn.execute('SELECT id FROM pokemon WHERE id=species_id')
        return len(cursor.fetchall())










