import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import xml.etree.ElementTree as ET
import os
import json
from collections import defaultdict
from datetime import datetime

# JSON 기반 동적 속성 로딩 시스템 🚀
class AttributeManager:
    """OOTP 속성 관리 클래스 - JSON 기반으로 모든 속성을 동적 로딩"""
    
    def __init__(self, json_file='ootp_attributes.json'):
        self.json_file = json_file
        self.data = self.load_attributes()
    
    def load_attributes(self):
        """JSON 파일에서 속성 데이터 로드"""
        try:
            if os.path.exists(self.json_file):
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"✅ {self.json_file} 로드 완료!")
                    print(f"📊 총 속성: 스토리라인({len(data.get('storyline_attributes', []))}), 기사({len(data.get('article_attributes', {}).get('all', []))}), 참여자({len(data.get('data_object_attributes', {}).get('all', []))})")
                    return data
            else:
                print(f"⚠️ {self.json_file} 파일이 없습니다. 기본값 사용.")
                return self.get_default_attributes()
        except Exception as e:
            print(f"❌ JSON 로드 실패: {e}")
            return self.get_default_attributes()
    
    def get_default_attributes(self):
        """JSON 파일이 없을 때 기본 속성 (최소한의 기능 보장)"""
        return {
            "storyline_attributes": ['random_frequency', 'league_year_min', 'league_year_max'],
            "article_attributes": {"all": [], "categories": {"MODIFIER": [], "CONDITION": [], "INJURY": [], "OTHER": []}, "types": {}},
            "data_object_types": ['PLAYER', 'TEAM', 'MANAGER'],
            "data_object_attributes": {"all": [], "by_type": {}, "types": {}},
            "tooltips": {},
            "presets": {}
        }
    
    @property
    def storyline_attributes(self):
        return self.data.get('storyline_attributes', [])
    
    @property
    def article_attributes(self):
        return self.data.get('article_attributes', {}).get('all', [])
    
    @property
    def article_categories(self):
        return self.data.get('article_attributes', {}).get('categories', {})
    
    @property
    def data_object_types(self):
        return self.data.get('data_object_types', [])
    
    @property
    def data_object_attributes(self):
        return self.data.get('data_object_attributes', {})
    
    def get_attributes_for_type(self, obj_type):
        """특정 타입의 속성들 반환 (공통 + 타입별)"""
        by_type = self.data_object_attributes.get('by_type', {})
        common = self.data_object_attributes.get('common', [])
        specific = by_type.get(obj_type, [])
        
        # 중복 제거하고 정렬
        all_attrs = list(set(common + specific))
        return sorted(all_attrs)
    
    def get_tooltip(self, attr_name):
        """속성의 한국어 툴팁 설명 반환"""
        return self.data.get('tooltips', {}).get(attr_name, attr_name)
    
    def get_presets(self, category):
        """카테고리별 프리셋 반환"""
        return self.data.get('presets', {}).get(category, {})
    
    def get_attribute_type(self, attr_name):
        """속성의 입력 타입 반환 (text, number, boolean)"""
        article_types = self.data.get('article_attributes', {}).get('types', {})
        data_types = self.data_object_attributes.get('types', {})
        
        return article_types.get(attr_name) or data_types.get(attr_name, 'text')

# 🌟 전역 속성 매니저 인스턴스 생성
ATTR_MANAGER = AttributeManager()

# 하위 호환성을 위한 상수들 (기존 코드와의 호환성 보장)
STORYLINE_ATTRIBUTES = ATTR_MANAGER.storyline_attributes
DATA_OBJECT_TYPES = ATTR_MANAGER.data_object_types
ARTICLE_MODIFIERS = ATTR_MANAGER.article_categories.get('MODIFIER', [])

# JSON에서 동적으로 로드되는 카테고리들
ARTICLE_CONDITIONS = ATTR_MANAGER.article_categories.get('CONDITION', [])

ARTICLE_INJURY = ATTR_MANAGER.article_categories.get('INJURY', [])
ARTICLE_OTHER = ATTR_MANAGER.article_categories.get('OTHER', [])

class ModernOOTPStorylineGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OOTP 스토리라인 생성기")
        self.root.geometry("1200x800")
        
        # OOTP 스타일 테마 설정
        self.setup_ootp_theme()
        
        # 데이터 저장소
        self.storylines = []
        self.current_file = None
        self.current_storyline_index = None
        
        # XML 구조 분석 데이터
        self.xml_structure = {
            'storyline_attributes': set(),
            'article_attributes': set(),
            'data_object_types': set(),
            'data_object_attributes': set()
        }
        
        # UI 구성
        self.setup_ui()
        
    def setup_ootp_theme(self):
        """OOTP 게임 스타일 테마 설정"""
        # OOTP 색상 팔레트
        self.colors = {
            'bg_primary': '#2b2b2b',        # 메인 배경 (어두운 회색)
            'bg_secondary': '#3c3c3c',      # 보조 배경
            'bg_field': '#1a4d1a',          # 야구장 그린 (어두운)
            'bg_dirt': '#8B4513',           # 야구장 흙색
            'text_primary': '#ffffff',       # 메인 텍스트 (흰색)
            'text_secondary': '#cccccc',     # 보조 텍스트 (밝은 회색)
            'text_accent': '#ffa500',        # 강조 텍스트 (주황색)
            'button_normal': '#4a4a4a',      # 일반 버튼
            'button_hover': '#5a5a5a',       # 버튼 호버
            'button_pressed': '#6a6a6a',     # 버튼 눌림
            'highlight': '#32CD32',          # 하이라이트 (밝은 녹색)
            'select': '#228B22',             # 선택 (진한 녹색)
            'border': '#666666',             # 테두리
            'error': '#ff4444',              # 에러 (빨간색)
            'warning': '#ffaa00',            # 경고 (노란색)
            'success': '#44ff44'             # 성공 (녹색)
        }
        
        # 루트 윈도우 배경색 설정
        self.root.configure(bg=self.colors['bg_primary'])
        
        # ttk 스타일 설정
        style = ttk.Style()
        
        # 테마 베이스 설정 (가능한 어두운 테마 사용)
        try:
            # 가능한 테마 확인
            available_themes = style.theme_names()
            if 'clam' in available_themes:
                style.theme_use('clam')
            elif 'alt' in available_themes:
                style.theme_use('alt')
        except:
            pass
        
        # 커스텀 스타일 설정
        self.setup_widget_styles(style)
        
        # 폰트 설정
        self.setup_fonts()
    
    def setup_widget_styles(self, style):
        """위젯별 스타일 설정"""
        # Frame 스타일
        style.configure('TFrame', 
                       background=self.colors['bg_primary'],
                       borderwidth=1,
                       relief='flat')
        
        # LabelFrame 스타일 
        style.configure('TLabelframe', 
                       background=self.colors['bg_primary'],
                       foreground=self.colors['text_primary'],
                       borderwidth=2,
                       relief='groove')
        style.configure('TLabelframe.Label',
                       background=self.colors['bg_primary'],
                       foreground=self.colors['text_accent'],
                       font=('Arial', 10, 'bold'))
        
        # Label 스타일
        style.configure('TLabel',
                       background=self.colors['bg_primary'],
                       foreground=self.colors['text_primary'],
                       font=('Arial', 10))
        
        # Button 스타일
        style.configure('TButton',
                       background=self.colors['button_normal'],
                       foreground=self.colors['text_primary'],
                       borderwidth=1,
                       focuscolor='none',
                       font=('Arial', 10, 'bold'))
        style.map('TButton',
                 background=[('active', self.colors['button_hover']),
                           ('pressed', self.colors['button_pressed'])])
        
        # Entry 스타일
        style.configure('TEntry',
                       fieldbackground=self.colors['bg_secondary'],
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['text_primary'],
                       borderwidth=1,
                       insertcolor=self.colors['text_primary'])
        
        # Combobox 스타일
        style.configure('TCombobox',
                       fieldbackground=self.colors['bg_secondary'],
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['text_primary'],
                       borderwidth=1)
        
        # Treeview 스타일
        style.configure('Treeview',
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['text_primary'],
                       fieldbackground=self.colors['bg_secondary'],
                       borderwidth=1)
        style.configure('Treeview.Heading',
                       background=self.colors['bg_field'],
                       foreground=self.colors['text_primary'],
                       relief='raised',
                       borderwidth=1,
                       font=('Arial', 10, 'bold'))
        style.map('Treeview',
                 background=[('selected', self.colors['select'])],
                 foreground=[('selected', self.colors['text_primary'])])
        
        # Checkbutton 스타일
        style.configure('TCheckbutton',
                       background=self.colors['bg_primary'],
                       foreground=self.colors['text_primary'],
                       focuscolor='none',
                       font=('Arial', 10))
        
        # Radiobutton 스타일
        style.configure('TRadiobutton',
                       background=self.colors['bg_primary'],
                       foreground=self.colors['text_primary'],
                       focuscolor='none',
                       font=('Arial', 10))
        
        # Text widget 스타일 (tkinter Text 위젯용)
        self.text_config = {
            'bg': self.colors['bg_secondary'],
            'fg': self.colors['text_primary'],
            'insertbackground': self.colors['text_primary'],
            'selectbackground': self.colors['select'],
            'selectforeground': self.colors['text_primary'],
            'font': ('Consolas', 10)
        }
        
        # Listbox 스타일
        self.listbox_config = {
            'bg': self.colors['bg_secondary'],
            'fg': self.colors['text_primary'],
            'selectbackground': self.colors['select'],
            'selectforeground': self.colors['text_primary'],
            'font': ('Arial', 10)
        }
    
    def setup_fonts(self):
        """폰트 설정"""
        self.fonts = {
            'title': ('Arial', 16, 'bold'),
            'heading': ('Arial', 12, 'bold'),
            'normal': ('Arial', 10),
            'small': ('Arial', 9),
            'code': ('Consolas', 10)
        }
        
    def setup_ui(self):
        """메인 UI 구성"""
        # 메인 프레임
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 상태바 프레임
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # 상태바 라벨
        self.status_label = ttk.Label(status_frame, text="준비됨", relief='sunken', padding="5")
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 진행률 표시 (필요시 사용)
        self.progress_var = tk.StringVar(value="")
        progress_label = ttk.Label(status_frame, textvariable=self.progress_var, relief='sunken', padding="5")
        progress_label.pack(side=tk.RIGHT)
        
        # 첫 화면 (스토리라인 목록)
        self.setup_main_screen()
        
        # 편집 화면 (스토리라인 편집)
        self.setup_edit_screen()
        
        # 초기 화면 설정
        self.show_main_screen()
        
        # 키보드 단축키 설정
        self.setup_keyboard_shortcuts()
        
    def setup_main_screen(self):
        """메인 화면 (스토리라인 목록) 설정"""
        self.main_screen = ttk.Frame(self.main_frame)
        
        # 헤더
        header_frame = ttk.Frame(self.main_screen)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(header_frame, text="⚾ OOTP 스토리라인 생성기", 
                               font=self.fonts['title'])
        title_label.pack(side=tk.LEFT)
        
        self.file_info_label = ttk.Label(header_frame, text="파일이 로드되지 않음")
        self.file_info_label.pack(side=tk.RIGHT)
        
        # 버튼 프레임
        button_frame = ttk.Frame(self.main_screen)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="📂 XML 열기", command=self.open_xml_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="💾 저장", command=self.save_as_xml).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="➕ 새 스토리라인 추가", command=self.add_new_storyline).pack(side=tk.LEFT, padx=(0, 5))
        
        # 스토리라인 목록
        list_frame = ttk.LabelFrame(self.main_screen, text="📋 스토리라인 목록", padding="5")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 트리뷰
        columns = ('ID', '제목', '빈도', '시즌', '상태')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=25)
        
        # 컬럼 설정
        column_widths = {'ID': 80, '제목': 400, '빈도': 60, '시즌': 80, '상태': 60}
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100))
        
        # 스크롤바
        tree_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 더블클릭 이벤트
        self.tree.bind('<Double-1>', self.on_storyline_double_click)
        
        # 상태바
        self.statusbar = ttk.Frame(self.main_screen)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        
        self.status_label = ttk.Label(self.statusbar, text="준비됨")
        self.status_label.pack(side=tk.LEFT)
        
        help_link = ttk.Label(self.statusbar, text="도움말", foreground='blue', cursor='hand2')
        help_link.pack(side=tk.RIGHT)
        help_link.bind('<Button-1>', lambda e: self.show_help())
        
    def setup_edit_screen(self):
        """편집 화면 설정"""
        self.edit_screen = ttk.Frame(self.main_frame)
        
        # 헤더
        edit_header = ttk.Frame(self.edit_screen)
        edit_header.pack(fill=tk.X, pady=(0, 10))
        
        self.edit_title_label = ttk.Label(edit_header, text="스토리라인 편집", font=self.fonts['heading'])
        self.edit_title_label.pack(side=tk.LEFT)
        
        ttk.Button(edit_header, text="← 목록으로 돌아가기", command=self.show_main_screen).pack(side=tk.RIGHT)
        
        # 편집 영역
        edit_frame = ttk.Frame(self.edit_screen)
        edit_frame.pack(fill=tk.BOTH, expand=True)
        
        # 왼쪽: 기본 정보
        left_frame = ttk.LabelFrame(edit_frame, text="기본 정보", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # 기본 정보 입력 필드들
        self.setup_basic_info_fields(left_frame)
        
        # 중앙: 기사 내용
        center_frame = ttk.LabelFrame(edit_frame, text="기사 내용", padding="10")
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 5))
        
        self.setup_article_fields(center_frame)
        
        # 하단 버튼
        button_frame = ttk.Frame(self.edit_screen)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="💾 저장", command=self.save_storyline).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="🗑️ 삭제", command=self.delete_current_storyline).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="❌ 취소", command=self.show_main_screen).pack(side=tk.LEFT)
        
    def setup_basic_info_fields(self, parent):
        """기본 정보 입력 필드 설정"""
        # 스크롤 가능한 프레임
        canvas = tk.Canvas(parent, height=600, bg=self.colors['bg_secondary'])  # 최소 높이 설정 및 테마 적용
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        row = 0
        
        # ID
        ttk.Label(scrollable_frame, text="ID:", font=self.fonts['normal']).grid(row=row, column=0, sticky=tk.W, pady=2)
        self.id_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.id_var, width=30).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        row += 1
        
        # 빈도
        ttk.Label(scrollable_frame, text="빈도:", font=self.fonts['normal']).grid(row=row, column=0, sticky=tk.W, pady=2)
        self.frequency_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.frequency_var, width=30).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        row += 1
        
        # 최소 연도
        ttk.Label(scrollable_frame, text="최소 연도:", font=self.fonts['normal']).grid(row=row, column=0, sticky=tk.W, pady=2)
        self.year_min_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.year_min_var, width=30).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        row += 1
        
        # 최대 연도
        ttk.Label(scrollable_frame, text="최대 연도:", font=self.fonts['normal']).grid(row=row, column=0, sticky=tk.W, pady=2)
        self.year_max_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.year_max_var, width=30).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        row += 1
        
        # 최소 사용 간격
        ttk.Label(scrollable_frame, text="최소 사용 간격 (일):", font=self.fonts['normal']).grid(row=row, column=0, sticky=tk.W, pady=2)
        self.interval_var = tk.StringVar()
        ttk.Entry(scrollable_frame, textvariable=self.interval_var, width=30).grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        row += 1
        
        # 트리거 이벤트
        ttk.Label(scrollable_frame, text="트리거 이벤트:", font=self.fonts['normal']).grid(row=row, column=0, sticky=tk.W, pady=2)
        self.trigger_var = tk.StringVar()
        trigger_combo = ttk.Combobox(scrollable_frame, textvariable=self.trigger_var, 
                                    values=["", "PLAYER_DEBUT", "PLAYER_RETIREMENT", "PLAYER_INJURY", "PLAYER_RECOVERY", 
                                           "PLAYER_TRADE", "PLAYER_SIGNING", "PLAYER_RELEASE", "PLAYER_CALLUP", 
                                           "PLAYER_SENDDOWN", "PLAYER_SUSPENSION", "PLAYER_AWARD", "PLAYER_MILESTONE",
                                           "TEAM_CHAMPIONSHIP", "TEAM_PLAYOFF_ENTRY", "TEAM_PLAYOFF_ELIMINATION",
                                           "TEAM_SEASON_START", "TEAM_SEASON_END", "TEAM_TRADE_DEADLINE",
                                           "MANAGER_HIRED", "MANAGER_FIRED", "MANAGER_RESIGNATION",
                                           "OWNER_CHANGE", "STADIUM_OPENING", "STADIUM_CLOSING",
                                           "LEAGUE_EXPANSION", "LEAGUE_CONTRACTION", "ALL_STAR_GAME",
                                           "WORLD_SERIES", "PLAYOFF_SERIES", "REGULAR_SEASON_GAME"],
                                    width=27, state="readonly")
        trigger_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2, padx=(10, 0))
        row += 1
        
        # 옵션들
        ttk.Label(scrollable_frame, text="옵션:", font=self.fonts['heading']).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        row += 1
        
        # 체크박스들
        self.season_var = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text="시즌 중만", variable=self.season_var).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
        row += 1
        
        self.offseason_var = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text="오프시즌만", variable=self.offseason_var).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
        row += 1
        
        self.spring_var = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text="스프링캠프만", variable=self.spring_var).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
        row += 1
        
        self.minor_var = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text="마이너리그", variable=self.minor_var).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
        row += 1
        
        self.once_var = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text="한 번만 발생", variable=self.once_var).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
        row += 1
        
        # 참여 인물 (REQUIRED_DATA) 섹션
        ttk.Label(scrollable_frame, text="참여 인물 (REQUIRED_DATA):", font=self.fonts['heading']).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(15, 5))
        row += 1
        
        # 참여 인물 리스트 프레임
        required_data_frame = ttk.LabelFrame(scrollable_frame, text="이벤트 참여자 설정", padding="10")
        required_data_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=5)
        row += 1
        
        # 참여 인물 리스트박스
        list_frame = ttk.Frame(required_data_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(list_frame, text="현재 참여자:", font=self.fonts['small']).pack(anchor=tk.W)
        
        # 리스트박스와 스크롤바
        listbox_frame = ttk.Frame(list_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.required_data_listbox = tk.Listbox(listbox_frame, height=4, **self.listbox_config)
        scrollbar_req = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.required_data_listbox.yview)
        self.required_data_listbox.configure(yscrollcommand=scrollbar_req.set)
        
        self.required_data_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_req.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 버튼 프레임
        btn_frame = ttk.Frame(required_data_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="➕ 인물 추가", command=self.add_required_data).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="✏️ 수정", command=self.edit_required_data).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="🗑️ 삭제", command=self.delete_required_data).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="🎭 주인공 설정", command=self.set_main_actor).pack(side=tk.LEFT, padx=(0, 5))
        
        # 도움말 라벨
        help_label = ttk.Label(required_data_frame, 
                              text="💡 팁: PLAYER, MANAGER, TEAM 등의 인물을 추가하여 스토리라인 발생 조건을 설정하세요.", 
                              font=('Arial', 8), foreground='gray', wraplength=400)
        help_label.pack(pady=(5, 0))
        
        # 참여 인물 데이터 저장소
        self.required_data_list = []
        
        scrollable_frame.columnconfigure(1, weight=1)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def setup_article_fields(self, parent):
        """기사 내용 입력 필드 설정 - 118개 속성을 카테고리별 탭으로 구성"""
        # 기사 선택 프레임
        article_select_frame = ttk.Frame(parent)
        article_select_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(article_select_frame, text="기사 선택:", font=self.fonts['heading']).pack(side=tk.LEFT)
        self.article_combo = ttk.Combobox(article_select_frame, width=20, state="readonly")
        self.article_combo.pack(side=tk.LEFT, padx=(5, 0))
        self.article_combo.bind('<<ComboboxSelected>>', self.on_article_select)
        
        ttk.Button(article_select_frame, text="➕ 새 기사", command=self.add_new_article).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(article_select_frame, text="🗑️ 삭제", command=self.delete_current_article).pack(side=tk.LEFT, padx=(5, 0))
        
        # 기사 기본 정보 프레임
        basic_info_frame = ttk.LabelFrame(parent, text="기사 기본 정보", padding="10")
        basic_info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 기사 ID
        id_frame = ttk.Frame(basic_info_frame)
        id_frame.pack(fill=tk.X, pady=2)
        ttk.Label(id_frame, text="기사 ID:", font=self.fonts['normal'], width=15).pack(side=tk.LEFT)
        self.article_id_var = tk.StringVar()
        ttk.Entry(id_frame, textvariable=self.article_id_var, width=20).pack(side=tk.LEFT, padx=(5, 0))
        
        # 제목
        subject_frame = ttk.Frame(basic_info_frame)
        subject_frame.pack(fill=tk.X, pady=2)
        ttk.Label(subject_frame, text="제목:", font=self.fonts['normal'], width=15).pack(side=tk.LEFT)
        self.subject_var = tk.StringVar()
        ttk.Entry(subject_frame, textvariable=self.subject_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # 부상 설명
        injury_frame = ttk.Frame(basic_info_frame)
        injury_frame.pack(fill=tk.X, pady=2)
        ttk.Label(injury_frame, text="부상 설명:", font=self.fonts['normal'], width=15).pack(side=tk.LEFT)
        self.injury_var = tk.StringVar()
        ttk.Entry(injury_frame, textvariable=self.injury_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # 기사 속성 저장을 위한 딕셔너리 (탭 설정 전에 초기화)
        self.article_attributes = {}
        self.article_bool_vars = {}  # Boolean 변수들 별도 저장
        
        # 내용 및 속성 탭 노트북
        self.article_notebook = ttk.Notebook(parent)
        self.article_notebook.pack(fill=tk.BOTH, expand=True)
        
        # 내용 탭
        self.setup_content_tab()
        
        # OOTP 속성 탭들
        self.setup_modifier_tab()
        self.setup_condition_tab()
        self.setup_injury_tab()
        self.setup_other_tab()
        
        # 현재 편집 중인 기사 인덱스
        self.current_article_index = 0
    
    def setup_content_tab(self):
        """기사 내용 탭 설정"""
        content_tab = ttk.Frame(self.article_notebook)
        self.article_notebook.add(content_tab, text="📝 내용")
        
        # 내용 입력 프레임
        content_frame = ttk.Frame(content_tab)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(1, weight=1)
        
        # OOTP 태그 버튼들
        tags_frame = ttk.LabelFrame(content_frame, text="OOTP 태그", padding="5")
        tags_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 태그 버튼들 배치
        tag_buttons = [
            ("👤 인물", "[%personlink#1 f l]", "인물 링크 삽입 (이름 성)"),
            ("👤 인물(성)", "[%personlink#1 l]", "인물 링크 삽입 (성만)"),
            ("🏆 팀", "[%teamlink#1]", "팀 링크 삽입"), 
            ("🏙️ 도시", "[%citylink#1]", "도시 링크 삽입"),
            ("📊 통계", "[%statlink#1]", "통계 링크 삽입"),
            ("📅 날짜", "[%datelink#1]", "날짜 링크 삽입"),
            ("⚾ 리그", "[%leaguelink#1]", "리그 링크 삽입"),
            ("🏟️ 구장", "[%stadiumlink#1]", "구장 링크 삽입"),
            ("🎖️ 상", "[%awardlink#1]", "상 링크 삽입"),
            ("💰 연봉", "[%salarylink#1]", "연봉 링크 삽입"),
            ("📈 기록", "[%recordlink#1]", "기록 링크 삽입"),
            ("🎯 나이", "[%agelink#1]", "나이 링크 삽입")
        ]
        
        for i, (text, tag, tooltip) in enumerate(tag_buttons):
            row_num = i // 4
            col_num = i % 4
            btn = ttk.Button(tags_frame, text=text, width=12,
                           command=lambda t=tag: self.insert_tag(t))
            btn.grid(row=row_num, column=col_num, padx=2, pady=2, sticky=tk.W)
            # 툴팁 효과 (간단한 상태바 업데이트)
            btn.bind('<Enter>', lambda e, tip=tooltip: self.update_status(tip))
            btn.bind('<Leave>', lambda e: self.update_status("준비됨"))
        
        # 태그 번호 변경 도구
        tag_tools_frame = ttk.Frame(content_frame)
        tag_tools_frame.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(tag_tools_frame, text="태그 번호:", font=('Arial', 9)).grid(row=0, column=0, sticky=tk.W)
        self.tag_number_var = tk.StringVar(value="1")
        tag_number_spin = ttk.Spinbox(tag_tools_frame, from_=1, to=10, width=5, 
                                     textvariable=self.tag_number_var)
        tag_number_spin.grid(row=0, column=1, padx=(5, 0))
        
        ttk.Button(tag_tools_frame, text="🔄 번호 변경", width=12,
                  command=self.update_tag_numbers).grid(row=1, column=0, columnspan=2, pady=5)
        
        # 내용 프레임의 컬럼 구성 조정
        content_frame.columnconfigure(1, weight=0)
        
        self.text_widget = scrolledtext.ScrolledText(content_frame, width=60, height=30, wrap=tk.WORD, **self.text_config)
        self.text_widget.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def setup_modifier_tab(self):
        """게임 효과 modifier 탭 설정 (24개)"""
        modifier_tab = ttk.Frame(self.article_notebook)
        self.article_notebook.add(modifier_tab, text="⚡ 게임 효과")
        
        self.create_attribute_grid(modifier_tab, ARTICLE_MODIFIERS, "게임에 미치는 직접적인 효과")
        
    def setup_condition_tab(self):
        """발생 조건 탭 설정 (71개)"""
        condition_tab = ttk.Frame(self.article_notebook)
        self.article_notebook.add(condition_tab, text="🎯 발생 조건")
        
        self.create_attribute_grid(condition_tab, ARTICLE_CONDITIONS, "이 기사가 나타나기 위한 조건")
        
    def setup_injury_tab(self):
        """부상/특수 효과 탭 설정 (5개)"""
        injury_tab = ttk.Frame(self.article_notebook)
        self.article_notebook.add(injury_tab, text="🏥 부상/특수")
        
        self.create_attribute_grid(injury_tab, ARTICLE_INJURY, "부상, 은퇴, 출전정지 등 특수 효과")
        
    def setup_other_tab(self):
        """기타 속성 탭 설정 (18개)"""
        other_tab = ttk.Frame(self.article_notebook)
        self.article_notebook.add(other_tab, text="🔧 기타")
        
        self.create_attribute_grid(other_tab, ARTICLE_OTHER, "시간 제한, 연결 기사 등 기타 설정")
    
    def create_attribute_grid(self, parent, attributes, description):
        """속성 그리드 생성 - 검색/필터 기능 포함"""
        # 설명 및 검색 프레임
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        ttk.Label(header_frame, text=description, font=('Arial', 9), foreground='gray').pack(side=tk.LEFT)
        
        # 검색 박스
        search_frame = ttk.Frame(header_frame)
        search_frame.pack(side=tk.RIGHT)
        
        ttk.Label(search_frame, text="🔍 검색:", font=('Arial', 8)).pack(side=tk.LEFT)
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var, width=15, font=('Arial', 8))
        search_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # 활성 속성만 보기 체크박스
        show_active_var = tk.BooleanVar()
        show_active_check = ttk.Checkbutton(search_frame, text="설정된 것만", variable=show_active_var, 
                                           command=lambda: self.filter_attributes(parent, attributes, search_var.get(), show_active_var.get()))
        show_active_check.pack(side=tk.LEFT, padx=(10, 0))
        
        # 프리셋 버튼들
        preset_frame = ttk.Frame(header_frame)
        preset_frame.pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Label(preset_frame, text="📋 프리셋:", font=('Arial', 8)).pack(side=tk.LEFT)
        presets = self.get_attribute_presets(attributes)
        for preset_name, preset_attrs in presets.items():
            preset_btn = ttk.Button(preset_frame, text=preset_name, width=8,
                                   command=lambda p=preset_attrs: self.apply_preset(p))
            preset_btn.pack(side=tk.LEFT, padx=(2, 0))
            self.create_tooltip(preset_btn, f"{preset_name} 관련 속성들을 자동 설정")
        
        # 속성 통계
        stats_label = ttk.Label(header_frame, text=f"총 {len(attributes)}개", font=('Arial', 8), foreground='blue')
        stats_label.pack(side=tk.RIGHT, padx=(10, 0))
        
        # 스크롤 가능한 프레임
        canvas = tk.Canvas(parent, height=500, bg=self.colors['bg_secondary'])  # 높이 설정 및 테마 적용
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 검색 이벤트 바인딩
        search_var.trace('w', lambda *args: self.filter_attributes(scrollable_frame, attributes, search_var.get(), show_active_var.get(), stats_label))
        
        # 속성 필드들과 프레임들 저장 (필터링용)
        attr_frames = {}
        
        # 중요도별 속성 분류
        important_attrs = [attr for attr in attributes if 'modifier' in attr or attr in ['injury', 'retirement', 'suspension']]
        common_attrs = [attr for attr in attributes if attr.endswith('_min') or attr.endswith('_max') or 'personality' in attr or 'quality' in attr]
        other_attrs = [attr for attr in attributes if attr not in important_attrs and attr not in common_attrs]
        
        # 중요도 순으로 정렬
        sorted_attributes = important_attrs + common_attrs + other_attrs
        
        # 속성 필드들 생성
        row = 0
        col = 0
        max_cols = 2  # 2열로 배치
        
        for attr in sorted_attributes:
            # 중요도에 따른 색상 설정
            if attr in important_attrs:
                frame_style = {'relief': 'solid', 'borderwidth': 2}
                label_color = 'red'
            elif attr in common_attrs:
                frame_style = {'relief': 'raised', 'borderwidth': 1}
                label_color = 'blue'
            else:
                frame_style = {'relief': 'flat', 'borderwidth': 1}
                label_color = 'gray'
            
            attr_frame = ttk.LabelFrame(scrollable_frame, text=attr, padding="5")
            attr_frame.grid(row=row, column=col, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
            attr_frames[attr] = attr_frame
            
            # StringVar 생성 및 저장
            var = tk.StringVar()
            self.article_attributes[attr] = var
            
            # 툴팁 생성 (한국어 설명)
            tooltip_text = self.get_attribute_tooltip(attr)
            self.create_tooltip(attr_frame, tooltip_text)
            
            # 속성 타입에 따른 위젯 선택 - JSON에서 동적 결정
            attr_type = ATTR_MANAGER.get_attribute_type(attr)
            if attr_type == 'boolean':
                # Boolean 타입 (체크박스) - StringVar로 "1"/"0" 처리
                bool_var = tk.BooleanVar()
                self.article_bool_vars[attr] = bool_var
                def on_bool_change(attr=attr, str_var=var, bool_var=bool_var):
                    str_var.set('1' if bool_var.get() else '0')
                bool_var.trace('w', lambda *args, attr=attr, str_var=var, bool_var=bool_var: on_bool_change(attr, str_var, bool_var))
                check_btn = ttk.Checkbutton(attr_frame, text="활성화", variable=bool_var)
                check_btn.pack(anchor=tk.W)
                # 시각적 피드백 추가
                def on_check_change(attr=attr, frame=attr_frame, bool_var=bool_var):
                    if bool_var.get():
                        frame.configure(relief='solid', borderwidth=2)
                    else:
                        frame.configure(relief='flat', borderwidth=1)
                bool_var.trace('w', lambda *args: on_check_change())
            elif attr_type == 'number' or 'modifier' in attr:
                # 숫자 입력 (Modifier 또는 일반 숫자)
                num_frame = ttk.Frame(attr_frame)
                num_frame.pack(fill=tk.X)
                
                if 'modifier' in attr:
                    # Modifier: -100~+100 범위
                    spinbox = ttk.Spinbox(num_frame, from_=-100, to=100, textvariable=var, width=8)
                    spinbox.pack(side=tk.LEFT)
                    ttk.Label(num_frame, text="(-100~+100)", font=('Arial', 7), foreground='gray').pack(side=tk.LEFT, padx=(5, 0))
                else:
                    # 일반 숫자: 0~999 범위
                    spinbox = ttk.Spinbox(num_frame, from_=0, to=999, textvariable=var, width=8)
                    spinbox.pack(side=tk.LEFT)
                    ttk.Label(num_frame, text="(0~999)", font=('Arial', 7), foreground='gray').pack(side=tk.LEFT, padx=(5, 0))
            else:
                # 일반 텍스트 입력
                ttk.Entry(attr_frame, textvariable=var, width=15).pack(anchor=tk.W)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # 필터링을 위해 프레임들 저장
        parent.attr_frames = attr_frames
        parent.attributes = attributes
        
        # 컬럼 가중치 설정
        for i in range(max_cols):
            scrollable_frame.columnconfigure(i, weight=1)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
    
    def filter_attributes(self, scrollable_frame, attributes, search_text, show_active_only, stats_label=None):
        """속성 필터링 기능"""
        if not hasattr(scrollable_frame.master, 'attr_frames'):
            return
            
        attr_frames = scrollable_frame.master.attr_frames
        visible_count = 0
        
        for attr_name, frame in attr_frames.items():
            should_show = True
            
            # 검색 텍스트 필터링
            if search_text and search_text.lower() not in attr_name.lower():
                should_show = False
                
            # 활성 속성만 보기 필터링
            if show_active_only and should_show:
                if attr_name in self.article_attributes:
                    value = self.article_attributes[attr_name].get()
                    if not value or value == '0':
                        should_show = False
            
            if should_show:
                frame.grid()
                visible_count += 1
            else:
                frame.grid_remove()
        
        # 통계 라벨 업데이트
        if stats_label:
            if search_text or show_active_only:
                stats_label.config(text=f"표시중 {visible_count}개 / 총 {len(attributes)}개")
            else:
                stats_label.config(text=f"총 {len(attributes)}개")
    
    def get_attribute_tooltip(self, attr):
        """속성별 한국어 툴팁 생성 - JSON에서 동적 로드"""
        tooltip = ATTR_MANAGER.get_tooltip(attr)
        if tooltip == attr:  # 기본값인 경우 (툴팁이 없는 경우)
            return f'{attr}\n(OOTP 속성 - 자세한 설명은 OOTP 매뉴얼 참조)'
        return tooltip
    
    def create_tooltip(self, widget, text):
        """툴팁 생성"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = ttk.Label(tooltip, text=text, background='lightyellow', 
                            relief='solid', borderwidth=1, font=('Arial', 8))
            label.pack()
            
            widget.tooltip = tooltip
            
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
                
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
    
    def get_attribute_presets(self, attributes):
        """속성 프리셋 정의 - JSON에서 동적 로드"""
        return ATTR_MANAGER.get_presets('ARTICLE')
    
    def apply_preset(self, preset_values):
        """프리셋 적용"""
        for attr_name, value in preset_values.items():
            if attr_name in self.article_attributes:
                var = self.article_attributes[attr_name]
                var.set(value)
                
                # Boolean 속성인 경우 체크박스도 업데이트
                if attr_name in self.article_bool_vars:
                    bool_var = self.article_bool_vars[attr_name]
                    bool_var.set(value == '1')
        
        self.show_status_message(f"프리셋이 적용되었습니다!", 2000)
    
    def show_status_message(self, message, duration=3000):
        """상태 메시지 표시"""
        if hasattr(self, 'status_label'):
            self.status_label.config(text=message, foreground='green')
            self.root.after(duration, lambda: self.status_label.config(text="준비됨", foreground='black'))
    
    def update_status(self, message):
        """상태 메시지 업데이트 (즉시)"""
        if hasattr(self, 'status_label'):
            self.status_label.config(text=message, foreground='black')
    
    def setup_keyboard_shortcuts(self):
        """키보드 단축키 설정"""
        # 전역 단축키
        self.root.bind('<Control-o>', lambda e: self.open_xml_file())  # Ctrl+O: 파일 열기
        self.root.bind('<Control-s>', lambda e: self.save_xml_file())  # Ctrl+S: 저장
        self.root.bind('<Control-n>', lambda e: self.add_new_storyline())  # Ctrl+N: 새 스토리라인
        self.root.bind('<Escape>', lambda e: self.show_main_screen())  # ESC: 메인화면으로
        self.root.bind('<F1>', lambda e: self.show_help())  # F1: 도움말
        self.root.bind('<F5>', lambda e: self.update_storyline_list())  # F5: 새로고침
        
        # 편집 모드 단축키
        self.root.bind('<Control-Return>', lambda e: self.save_storyline() if hasattr(self, 'current_storyline_index') else None)  # Ctrl+Enter: 스토리라인 저장
        self.root.bind('<Control-Delete>', lambda e: self.delete_current_storyline() if hasattr(self, 'current_storyline_index') else None)  # Ctrl+Del: 삭제
        
        # 메인 화면 단축키
        self.root.bind('<Delete>', lambda e: self.delete_selected_storyline_from_main())  # Del: 선택된 스토리라인 삭제
        self.root.bind('<Return>', lambda e: self.edit_selected_storyline_from_main())  # Enter: 선택된 스토리라인 편집
        
        # 기사 편집 단축키  
        self.root.bind('<Control-j>', lambda e: self.add_new_article() if hasattr(self, 'current_storyline_index') else None)  # Ctrl+J: 새 기사
        self.root.bind('<Control-d>', lambda e: self.delete_current_article() if hasattr(self, 'current_article_index') else None)  # Ctrl+D: 기사 삭제
        
        # 탭 전환 단축키
        self.root.bind('<Control-1>', lambda e: self.switch_article_tab(0))  # Ctrl+1: 내용 탭
        self.root.bind('<Control-2>', lambda e: self.switch_article_tab(1))  # Ctrl+2: 게임 효과 탭
        self.root.bind('<Control-3>', lambda e: self.switch_article_tab(2))  # Ctrl+3: 발생 조건 탭
        self.root.bind('<Control-4>', lambda e: self.switch_article_tab(3))  # Ctrl+4: 부상/특수 탭
        self.root.bind('<Control-5>', lambda e: self.switch_article_tab(4))  # Ctrl+5: 기타 탭
        
        # 단축키 도움말 추가
        self.keyboard_shortcuts_help = """
🎹 키보드 단축키:

📁 파일 작업:
• Ctrl+O: XML 파일 열기
• Ctrl+S: XML 파일 저장
• F5: 목록 새로고침

📝 스토리라인 편집:
• Ctrl+N: 새 스토리라인 추가
• Enter: 선택된 스토리라인 편집 (메인 화면)
• Ctrl+Enter: 현재 스토리라인 저장
• Delete: 선택된 스토리라인 삭제 (메인 화면)
• Ctrl+Delete: 현재 스토리라인 삭제
• ESC: 메인 화면으로 돌아가기

📰 기사 편집:
• Ctrl+J: 새 기사 추가
• Ctrl+D: 현재 기사 삭제

🎯 탭 전환:
• Ctrl+1: 📝 내용 탭
• Ctrl+2: ⚡ 게임 효과 탭  
• Ctrl+3: 🎯 발생 조건 탭
• Ctrl+4: 🏥 부상/특수 탭
• Ctrl+5: 🔧 기타 탭

❓ 기타:
• F1: 도움말 보기
        """
    
    def switch_article_tab(self, tab_index):
        """기사 편집 탭 전환"""
        if hasattr(self, 'article_notebook') and hasattr(self, 'current_storyline_index'):
            if self.current_storyline_index is not None:
                try:
                    self.article_notebook.select(tab_index)
                    self.show_status_message(f"탭 전환: {['내용', '게임 효과', '발생 조건', '부상/특수', '기타'][tab_index]}")
                except tk.TclError:
                    pass  # 탭이 존재하지 않으면 무시
    
    def add_required_data(self):
        """참여 인물 추가"""
        dialog = RequiredDataDialog(self.root, "참여 인물 추가")
        result = dialog.show()
        
        if result:
            self.required_data_list.append(result)
            self.update_required_data_list()
            self.show_status_message(f"{result['type']} 참여자가 추가되었습니다!")
    
    def edit_required_data(self):
        """참여 인물 수정"""
        selected = self.required_data_listbox.curselection()
        if not selected:
            messagebox.showwarning("선택 필요", "수정할 참여자를 선택해주세요.")
            return
        
        index = selected[0]
        current_data = self.required_data_list[index]
        
        dialog = RequiredDataDialog(self.root, "참여 인물 수정", current_data)
        result = dialog.show()
        
        if result:
            self.required_data_list[index] = result
            self.update_required_data_list()
            self.show_status_message(f"{result['type']} 참여자가 수정되었습니다!")
    
    def delete_required_data(self):
        """참여 인물 삭제"""
        selected = self.required_data_listbox.curselection()
        if not selected:
            messagebox.showwarning("선택 필요", "삭제할 참여자를 선택해주세요.")
            return
        
        index = selected[0]
        data = self.required_data_list[index]
        
        if messagebox.askyesno("삭제 확인", f"{data['type']} 참여자를 삭제하시겠습니까?"):
            del self.required_data_list[index]
            self.update_required_data_list()
            self.show_status_message(f"{data['type']} 참여자가 삭제되었습니다!")
    
    def set_main_actor(self):
        """주인공 설정"""
        selected = self.required_data_listbox.curselection()
        if not selected:
            messagebox.showwarning("선택 필요", "주인공을 설정할 참여자를 선택해주세요.")
            return
        
        # 기존 main_actor 제거
        for data in self.required_data_list:
            if 'main_actor' in data:
                del data['main_actor']
        
        # 선택된 항목을 주인공으로 설정
        index = selected[0]
        self.required_data_list[index]['main_actor'] = '1'
        self.update_required_data_list()
        self.show_status_message(f"{self.required_data_list[index]['type']}이(가) 주인공으로 설정되었습니다!")
    
    def update_required_data_list(self):
        """참여 인물 리스트 업데이트"""
        self.required_data_listbox.delete(0, tk.END)
        
        for i, data in enumerate(self.required_data_list):
            # 표시 텍스트 생성
            display_text = f"{data['type']}"
            
            # 주인공 표시
            if data.get('main_actor') == '1':
                display_text = f"🎭 {display_text} (주인공)"
            
            # 주요 조건들 표시
            conditions = []
            for key, value in data.items():
                if key not in ['type', 'main_actor'] and value:
                    if key.endswith('_min'):
                        conditions.append(f"{key.replace('_min', '')}≥{value}")
                    elif key.endswith('_max'):
                        conditions.append(f"{key.replace('_max', '')}≤{value}")
                    else:
                        conditions.append(f"{key}={value}")
            
            if conditions:
                display_text += f" ({', '.join(conditions[:3])}{'...' if len(conditions) > 3 else ''})"
            
            self.required_data_listbox.insert(tk.END, display_text)
    
    def insert_tag(self, tag):
        """OOTP 태그를 텍스트 위젯에 삽입"""
        if hasattr(self, 'text_widget'):
            # 현재 설정된 번호로 태그 업데이트
            current_number = self.tag_number_var.get()
            updated_tag = tag.replace("#1", f"#{current_number}")
            
            # 현재 커서 위치 가져오기
            cursor_pos = self.text_widget.index(tk.INSERT)
            # 태그 삽입
            self.text_widget.insert(cursor_pos, updated_tag)
            # 커서를 태그 끝으로 이동
            self.text_widget.mark_set(tk.INSERT, f"{cursor_pos} + {len(updated_tag)}c")
            # 텍스트 위젯에 포커스
            self.text_widget.focus_set()
    
    def update_tag_numbers(self):
        """선택된 텍스트의 태그 번호를 변경"""
        if hasattr(self, 'text_widget'):
            try:
                # 선택된 텍스트 확인
                selected_text = self.text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
                if selected_text:
                    # 태그 패턴 찾기 및 번호 변경
                    import re
                    new_number = self.tag_number_var.get()
                    
                    # [%...#숫자...] 패턴을 찾아서 번호 변경
                    pattern = r'(\[%\w+link#)(\d+)(\s*[^\]]*\])'
                    updated_text = re.sub(pattern, rf'\g<1>{new_number}\g<3>', selected_text)
                    
                    if updated_text != selected_text:
                        # 선택된 텍스트를 새로운 텍스트로 교체
                        self.text_widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                        self.text_widget.insert(tk.INSERT, updated_text)
                        messagebox.showinfo("완료", f"태그 번호가 {new_number}번으로 변경되었습니다.")
                    else:
                        messagebox.showinfo("정보", "선택된 텍스트에 변경할 수 있는 태그가 없습니다.")
                else:
                    messagebox.showinfo("정보", "태그 번호를 변경할 텍스트를 먼저 선택해주세요.")
            except tk.TclError:
                messagebox.showinfo("정보", "태그 번호를 변경할 텍스트를 먼저 선택해주세요.")
         
    def on_article_select(self, event):
        """기사 선택 이벤트"""
        if self.current_storyline_index is not None:
            selected_index = self.article_combo.current()
            if selected_index >= 0:
                self.current_article_index = selected_index
                self.load_article_to_fields()
         
    def add_new_article(self):
        """새 기사 추가"""
        if self.current_storyline_index is not None:
            storyline = self.storylines[self.current_storyline_index]
            new_article = {
                'id': f"article_{len(storyline['articles']) + 1}",
                'subject': '',
                'text': '',
                'injury_description': '',
                'modifiers': {}
            }
            storyline['articles'].append(new_article)
            self.update_article_combo()
            self.article_combo.set(len(storyline['articles']) - 1)
            self.current_article_index = len(storyline['articles']) - 1
            self.clear_article_fields()
         
    def delete_current_article(self):
        """현재 기사 삭제"""
        if self.current_storyline_index is not None and self.current_article_index >= 0:
            storyline = self.storylines[self.current_storyline_index]
            if len(storyline['articles']) > 1:
                if messagebox.askyesno("확인", "현재 기사를 삭제하시겠습니까?"):
                    del storyline['articles'][self.current_article_index]
                    self.update_article_combo()
                    if self.current_article_index >= len(storyline['articles']):
                        self.current_article_index = len(storyline['articles']) - 1
                    if storyline['articles']:
                        self.article_combo.set(self.current_article_index)
                        self.load_article_to_fields()
                    else:
                        self.clear_article_fields()
            else:
                messagebox.showwarning("경고", "최소 하나의 기사는 있어야 합니다.")
         
    def update_article_combo(self):
        """기사 콤보박스 업데이트"""
        if self.current_storyline_index is not None:
            storyline = self.storylines[self.current_storyline_index]
            article_names = [f"기사 {i+1}: {article['subject'][:30]}" if article['subject'] else f"기사 {i+1}" 
                           for i, article in enumerate(storyline['articles'])]
            self.article_combo['values'] = article_names
         
    def load_article_to_fields(self):
        """현재 기사 데이터를 필드에 로드 - 118개 속성 포함"""
        if self.current_storyline_index is not None and self.current_article_index >= 0:
            storyline = self.storylines[self.current_storyline_index]
            if self.current_article_index < len(storyline['articles']):
                article = storyline['articles'][self.current_article_index]
                
                # 기본 정보 로드
                self.article_id_var.set(article.get('id', ''))
                self.subject_var.set(article.get('subject', ''))
                self.injury_var.set(article.get('injury_description', ''))
                
                # 내용 로드
                if hasattr(self, 'text_widget'):
                    self.text_widget.delete(1.0, tk.END)
                    self.text_widget.insert(1.0, article.get('text', ''))
                
                # 모든 modifier 속성 로드
                modifiers = article.get('modifiers', {})
                for attr_name, var in self.article_attributes.items():
                    value = modifiers.get(attr_name, '')
                    var.set(str(value))
                    
                    # Boolean 타입 속성은 별도 처리
                    if attr_name in self.article_bool_vars:
                        bool_var = self.article_bool_vars[attr_name]
                        bool_var.set(value == '1')
         
    def clear_article_fields(self):
        """기사 필드 초기화 - 118개 속성 포함"""
        self.article_id_var.set('')
        self.subject_var.set('')
        self.injury_var.set('')
        
        if hasattr(self, 'text_widget'):
            self.text_widget.delete(1.0, tk.END)
        
        # 모든 속성 필드 초기화
        for var in self.article_attributes.values():
            var.set('')
            
        # Boolean 변수들도 초기화
        for bool_var in self.article_bool_vars.values():
            bool_var.set(False)
         
    def save_current_article(self):
        """현재 기사 저장 - 118개 속성 포함"""
        if self.current_storyline_index is not None and self.current_article_index >= 0:
            storyline = self.storylines[self.current_storyline_index]
            if self.current_article_index < len(storyline['articles']):
                article = storyline['articles'][self.current_article_index]
                
                # 기본 정보 저장
                article['id'] = self.article_id_var.get()
                article['subject'] = self.subject_var.get()
                article['injury_description'] = self.injury_var.get()
                
                # 내용 저장
                if hasattr(self, 'text_widget'):
                    article['text'] = self.text_widget.get(1.0, tk.END).strip()
                
                # 모든 modifier 속성 저장 (빈 값은 제외)
                modifiers = {}
                for attr_name, var in self.article_attributes.items():
                    value = var.get().strip()
                    if value:  # 빈 값이 아닌 경우만 저장
                        modifiers[attr_name] = value
                
                article['modifiers'] = modifiers
                self.update_article_combo()
        
    def show_main_screen(self):
        """메인 화면 표시"""
        self.edit_screen.pack_forget()
        self.main_screen.pack(fill=tk.BOTH, expand=True)
        self.update_storyline_list()
        
    def show_edit_screen(self, storyline_index):
        """편집 화면 표시"""
        self.current_storyline_index = storyline_index
        self.main_screen.pack_forget()
        self.edit_screen.pack(fill=tk.BOTH, expand=True)
        
        if storyline_index is not None:
            # 기존 스토리라인 편집
            storyline = self.storylines[storyline_index]
            self.edit_title_label.config(text=f"스토리라인 편집 - {storyline['id']}")
            self.load_storyline_to_fields(storyline)
        else:
            # 새 스토리라인 추가
            self.edit_title_label.config(text="새 스토리라인 추가")
            self.clear_fields()
        
    def load_storyline_to_fields(self, storyline):
        """스토리라인 데이터를 필드에 로드"""
        self.id_var.set(storyline['id'])
        self.frequency_var.set(storyline['random_frequency'])
        self.year_min_var.set(storyline['league_year_min'])
        self.year_max_var.set(storyline['league_year_max'])
        self.interval_var.set(storyline['min_usage_interval_days'])
        self.trigger_var.set(storyline['trigger_events'])
        
        self.season_var.set(storyline['only_in_season'] == '1')
        self.offseason_var.set(storyline['only_in_offseason'] == '1')
        self.spring_var.set(storyline['only_in_spring'] == '1')
        self.minor_var.set(storyline['is_minor_league'] == '1')
        self.once_var.set(storyline['storyline_happens_only_once'] == '1')
        
        # REQUIRED_DATA 로드
        self.required_data_list = storyline.get('required_data', []).copy()
        self.update_required_data_list()
        
        # 기사 정보 업데이트
        self.update_article_combo()
        if storyline['articles']:
            self.current_article_index = 0
            self.article_combo.set(0)
            self.load_article_to_fields()
        else:
            self.clear_article_fields()
        
    def clear_fields(self):
        """필드 초기화"""
        self.id_var.set('')
        self.frequency_var.set('1000')
        self.year_min_var.set('')
        self.year_max_var.set('')
        self.interval_var.set('')
        self.trigger_var.set('')
        
        self.season_var.set(False)
        self.offseason_var.set(False)
        self.spring_var.set(False)
        self.minor_var.set(False)
        self.once_var.set(False)
        
        # 기사 필드 초기화
        self.clear_article_fields()
        
        # REQUIRED_DATA 초기화
        self.required_data_list = []
        self.update_required_data_list()
        
    def save_storyline(self):
        """스토리라인 저장"""
        # 현재 기사 저장
        if self.current_storyline_index is not None:
            self.save_current_article()
        
        # 필드에서 데이터 수집
        storyline = {
            'id': self.id_var.get(),
            'random_frequency': self.frequency_var.get(),
            'league_year_min': self.year_min_var.get(),
            'league_year_max': self.year_max_var.get(),
            'only_in_season': '1' if self.season_var.get() else '',
            'only_in_offseason': '1' if self.offseason_var.get() else '',
            'only_in_spring': '1' if self.spring_var.get() else '',
            'is_minor_league': '1' if self.minor_var.get() else '',
            'storyline_happens_only_once': '1' if self.once_var.get() else '',
            'min_usage_interval_days': self.interval_var.get(),
            'trigger_events': self.trigger_var.get(),
            'required_data': self.required_data_list.copy(),  # REQUIRED_DATA 포함
            'articles': []
        }
        
        # 기존 기사들 복사
        if self.current_storyline_index is not None:
            storyline['articles'] = self.storylines[self.current_storyline_index]['articles'].copy()
        else:
            # 새 스토리라인의 경우 기본 기사 하나 추가
            storyline['articles'] = [{
                'id': self.article_id_var.get(),
                'subject': self.subject_var.get(),
                'text': self.text_widget.get(1.0, tk.END).strip(),
                'injury_description': self.injury_var.get(),
                'modifiers': {}
            }]
        
        if self.current_storyline_index is not None:
            # 기존 스토리라인 업데이트
            self.storylines[self.current_storyline_index] = storyline
            messagebox.showinfo("성공", "스토리라인이 수정되었습니다.")
        else:
            # 새 스토리라인 추가
            self.storylines.append(storyline)
            messagebox.showinfo("성공", "새 스토리라인이 추가되었습니다.")
        
        self.show_main_screen()
        
    def delete_current_storyline(self):
        """현재 스토리라인 삭제"""
        if self.current_storyline_index is not None:
            storyline = self.storylines[self.current_storyline_index]
            if messagebox.askyesno("확인", f"다음 스토리라인을 삭제하시겠습니까?\n\nID: {storyline['id']}\n제목: {storyline['articles'][0]['subject'] if storyline['articles'] else '제목 없음'}"):
                del self.storylines[self.current_storyline_index]
                messagebox.showinfo("성공", "스토리라인이 삭제되었습니다.")
                self.show_main_screen()
        else:
            messagebox.showinfo("정보", "새로 추가 중인 스토리라인은 삭제할 수 없습니다.")
    
    def delete_selected_storyline_from_main(self):
        """메인 화면에서 선택된 스토리라인 삭제 (Delete 키)"""
        # 메인 화면이 표시되고 있는지 확인
        if not hasattr(self, 'main_screen') or not self.main_screen.winfo_viewable():
            return
        
        # 트리뷰에서 선택된 항목 확인
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("선택 필요", "삭제할 스토리라인을 선택해주세요.")
            return
        
        # 선택된 항목의 인덱스 찾기
        selected_item = selection[0]
        selected_index = None
        
        # 트리뷰의 모든 항목을 순회하여 선택된 항목의 인덱스 찾기
        for i, item in enumerate(self.tree.get_children()):
            if item == selected_item:
                selected_index = i
                break
        
        if selected_index is None or selected_index >= len(self.storylines):
            messagebox.showerror("오류", "선택된 스토리라인을 찾을 수 없습니다.")
            return
        
        # 삭제할 스토리라인 정보
        storyline = self.storylines[selected_index]
        storyline_title = storyline['articles'][0]['subject'] if storyline['articles'] else '제목 없음'
        
        # 삭제 확인 대화상자 (더 자세한 정보 표시)
        confirm_message = f"""⚠️ 스토리라인 삭제 확인
        
다음 스토리라인을 정말 삭제하시겠습니까?

📄 ID: {storyline['id']}
📝 제목: {storyline_title}
🎯 빈도: {storyline.get('random_frequency', 'N/A')}
📊 기사 수: {len(storyline.get('articles', []))}개

⚠️ 이 작업은 되돌릴 수 없습니다!"""
        
        if messagebox.askyesno("🗑️ 삭제 확인", confirm_message):
            # 스토리라인 삭제
            del self.storylines[selected_index]
            
            # 목록 업데이트
            self.update_storyline_list()
            
            # 성공 메시지
            self.show_status_message(f"✅ 스토리라인 '{storyline['id']}'가 삭제되었습니다!")
            messagebox.showinfo("🎉 삭제 완료", f"스토리라인 '{storyline['id']}'가 성공적으로 삭제되었습니다.")
    
    def edit_selected_storyline_from_main(self):
        """메인 화면에서 선택된 스토리라인 편집 (Enter 키)"""
        # 메인 화면이 표시되고 있는지 확인
        if not hasattr(self, 'main_screen') or not self.main_screen.winfo_viewable():
            return
        
        # 트리뷰에서 선택된 항목 확인
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("선택 필요", "편집할 스토리라인을 선택해주세요.")
            return
        
        # 선택된 항목의 인덱스 찾기
        selected_item = selection[0]
        selected_index = None
        
        # 트리뷰의 모든 항목을 순회하여 선택된 항목의 인덱스 찾기
        for i, item in enumerate(self.tree.get_children()):
            if item == selected_item:
                selected_index = i
                break
        
        if selected_index is None or selected_index >= len(self.storylines):
            messagebox.showerror("오류", "선택된 스토리라인을 찾을 수 없습니다.")
            return
        
        # 스토리라인 편집 화면으로 이동
        self.show_edit_screen(selected_index)
        self.show_status_message(f"📝 스토리라인 '{self.storylines[selected_index]['id']}' 편집 중...")
        
    def on_storyline_double_click(self, event):
        """스토리라인 더블클릭 이벤트"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            storyline_id = item['values'][0]
            
            # 해당 스토리라인 찾기
            for i, storyline in enumerate(self.storylines):
                if storyline['id'] == storyline_id:
                    self.show_edit_screen(i)
                    break
        
    def update_status(self, message):
        """상태바 업데이트"""
        self.status_label.config(text=message)
        
    def update_file_info(self):
        """파일 정보 업데이트"""
        if self.current_file:
            filename = os.path.basename(self.current_file)
            count = len(self.storylines)
            self.file_info_label.config(text=f"📁 {filename} ({count}개)")
        else:
            self.file_info_label.config(text="파일이 로드되지 않음")
            
    def analyze_xml_structure(self, file_path):
        """XML 파일의 구조를 분석하여 실제 사용되는 속성들을 파악"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # 분석 데이터 초기화
            self.xml_structure = {
                'storyline_attributes': set(),
                'article_attributes': set(),
                'data_object_types': set(),
                'data_object_attributes': set()
            }
            
            # STORYLINE 요소들 분석
            for storyline in root.findall('STORYLINES/STORYLINE'):
                # STORYLINE 속성들 수집
                for attr in storyline.attrib:
                    self.xml_structure['storyline_attributes'].add(attr)
                
                # REQUIRED_DATA 분석
                for data_obj in storyline.findall('REQUIRED_DATA/DATA_OBJECT'):
                    obj_type = data_obj.get('type', '')
                    if obj_type:
                        self.xml_structure['data_object_types'].add(obj_type)
                    
                    for attr in data_obj.attrib:
                        if attr != 'type':  # type은 따로 관리
                            self.xml_structure['data_object_attributes'].add(attr)
                
                # ARTICLES 분석
                for article in storyline.findall('ARTICLES/ARTICLE'):
                    for attr in article.attrib:
                        self.xml_structure['article_attributes'].add(attr)
            
            print("XML 구조 분석 완료:")
            print(f"스토리라인 속성: {sorted(self.xml_structure['storyline_attributes'])}")
            print(f"기사 속성 ({len(self.xml_structure['article_attributes'])}개): {sorted(list(self.xml_structure['article_attributes'])[:20])}...")
            print(f"데이터 객체 타입: {sorted(self.xml_structure['data_object_types'])}")
            
        except Exception as e:
            print(f"XML 구조 분석 오류: {e}")

    def open_xml_file(self):
        """XML 파일 열기"""
        file_path = filedialog.askopenfilename(
            title="OOTP 스토리라인 XML 파일 선택",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.update_status("파일을 분석하는 중...")
                self.progress_var.set("단계 1/3")
                self.root.update()
                
                # 먼저 XML 구조 분석
                self.analyze_xml_structure(file_path)
                
                self.update_status("파일을 로드하는 중...")
                self.progress_var.set("단계 2/3")
                self.root.update()
                
                self.parse_xml_file(file_path)
                self.current_file = file_path
                
                self.update_status("목록을 업데이트하는 중...")
                self.progress_var.set("단계 3/3")
                self.root.update()
                
                self.update_file_info()
                self.update_status(f"파일을 성공적으로 로드했습니다: {os.path.basename(file_path)}")
                
                # 진행률 초기화
                self.root.after(2000, lambda: self.progress_var.set(""))
                
                # 분석 결과 출력
                article_attrs = len(self.xml_structure['article_attributes'])
                storyline_attrs = len(self.xml_structure['storyline_attributes'])
                data_types = len(self.xml_structure['data_object_types'])
                
                messagebox.showinfo("✅ 로드 완료", 
                    f"파일을 성공적으로 로드했습니다:\n{os.path.basename(file_path)}\n\n"
                    f"📊 분석 결과:\n"
                    f"• 스토리라인: {len(self.storylines)}개\n"
                    f"• 스토리라인 속성: {storyline_attrs}개\n"
                    f"• 기사 modifier 속성: {article_attrs}개\n"
                    f"• 데이터 객체 타입: {data_types}개\n\n"
                    f"🎉 이제 스토리라인을 더블클릭하여 편집하세요!")
            except Exception as e:
                self.update_status("파일 로드 실패")
                self.progress_var.set("")
                messagebox.showerror("❌ 오류", f"파일 로드 중 오류가 발생했습니다:\n{str(e)}")
    
    def parse_xml_file(self, file_path):
        """XML 파일 파싱"""
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        self.storylines = []
        
        storylines_elem = root.find('STORYLINES')
        if storylines_elem is None:
            raise ValueError("STORYLINES 태그를 찾을 수 없습니다.")
        
        for storyline_elem in storylines_elem.findall('STORYLINE'):
            storyline = self.parse_storyline_element(storyline_elem)
            self.storylines.append(storyline)
        
        # ID 순으로 정렬
        self.storylines.sort(key=lambda x: x['id'])
        
        # 목록 업데이트
        self.update_storyline_list()
        
    def parse_storyline_element(self, elem):
        """스토리라인 요소 파싱 - 실제 XML 구조에 맞게 모든 속성 처리"""
        storyline = {
            'required_data': [],
            'articles': []
        }
        
        # 모든 스토리라인 속성을 동적으로 파싱
        for attr_name, attr_value in elem.attrib.items():
            storyline[attr_name] = attr_value
        
        # 기본값 설정 (누락된 필수 속성들)
        defaults = {
            'id': '',
            'random_frequency': '',
            'league_year_min': '',
            'league_year_max': '',
            'only_in_season': '',
            'only_in_offseason': '',
            'only_in_spring': '',
            'is_minor_league': '',
            'storyline_happens_only_once': '',
            'min_usage_interval_days': '',
            'trigger_events': ''
        }
        
        for key, default_value in defaults.items():
            if key not in storyline:
                storyline[key] = default_value
        
        # REQUIRED_DATA 파싱
        required_data_elem = elem.find('REQUIRED_DATA')
        if required_data_elem is not None:
            for data_obj in required_data_elem.findall('DATA_OBJECT'):
                data = {}
                for key, value in data_obj.attrib.items():
                    data[key] = value
                storyline['required_data'].append(data)
        
        # ARTICLES 파싱
        articles_elem = elem.find('ARTICLES')
        if articles_elem is not None:
            for article_elem in articles_elem.findall('ARTICLE'):
                article = {
                    'id': article_elem.get('id', ''),
                    'subject': '',
                    'text': '',
                    'injury_description': '',
                    'modifiers': {}
                }
                
                subject_elem = article_elem.find('SUBJECT')
                if subject_elem is not None:
                    article['subject'] = subject_elem.text or ''
                
                text_elem = article_elem.find('TEXT')
                if text_elem is not None:
                    article['text'] = text_elem.text or ''
                
                injury_elem = article_elem.find('INJURY_DESCRIPTION')
                if injury_elem is not None:
                    article['injury_description'] = injury_elem.text or ''
                
                for key, value in article_elem.attrib.items():
                    if key not in ['id']:
                        article['modifiers'][key] = value
                
                storyline['articles'].append(article)
        
        return storyline
    
    def update_storyline_list(self):
        """스토리라인 목록 업데이트"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for storyline in self.storylines:
            title = storyline['articles'][0]['subject'] if storyline['articles'] else storyline['id']
            
            season_info = ""
            if storyline['only_in_season'] == '1':
                season_info = "시즌 중"
            elif storyline['only_in_offseason'] == '1':
                season_info = "오프시즌"
            elif storyline['only_in_spring'] == '1':
                season_info = "스프링캠프"
            else:
                season_info = "상시"
            
            # 상태 아이콘 - 기사 설정 여부만 확인
            has_articles = bool(storyline['articles'])
            has_article_content = False
            
            if has_articles:
                # 기사에 실제 내용이 있는지 확인
                for article in storyline['articles']:
                    if article.get('subject') or article.get('text'):
                        has_article_content = True
                        break
                        
            if has_articles and has_article_content:
                status = "✅"  # 완전 설정됨
            elif has_articles:
                status = "📝"  # 기사 있지만 내용 부족
            else:
                status = "⚠️"  # 미완성
            
            self.tree.insert('', 'end', values=(
                storyline['id'],
                title[:50] + "..." if len(title) > 50 else title,
                storyline['random_frequency'],
                season_info,
                status
            ))
    
    def add_new_storyline(self):
        """새 스토리라인 추가"""
        self.show_edit_screen(None)
    
    def save_as_xml(self):
        """XML로 저장"""
        if not self.storylines:
            messagebox.showwarning("경고", "저장할 스토리라인이 없습니다.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="XML 파일로 저장",
            defaultextension=".xml",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.update_status("파일을 저장하는 중...")
                self.create_xml_file(file_path)
                self.update_status(f"파일을 성공적으로 저장했습니다: {os.path.basename(file_path)}")
                messagebox.showinfo("성공", f"XML 파일로 저장되었습니다:\n{os.path.basename(file_path)}")
            except Exception as e:
                self.update_status("파일 저장 실패")
                messagebox.showerror("오류", f"저장 중 오류가 발생했습니다:\n{str(e)}")
    
    def create_xml_file(self, file_path):
        """XML 파일 생성"""
        root = ET.Element("STORYLINE_DATABASE")
        root.set("fileversion", f"OOTP Developments {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        storylines_elem = ET.SubElement(root, "STORYLINES")
        
        for storyline in self.storylines:
            storyline_elem = ET.SubElement(storylines_elem, "STORYLINE")
            storyline_elem.set("id", storyline['id'])
            
            attributes = [
                'random_frequency', 'league_year_min', 'league_year_max',
                'only_in_season', 'only_in_offseason', 'only_in_spring',
                'is_minor_league', 'storyline_happens_only_once',
                'min_usage_interval_days', 'trigger_events'
            ]
            
            for attr in attributes:
                if storyline[attr]:
                    storyline_elem.set(attr, storyline[attr])
            
            if storyline['required_data']:
                required_data_elem = ET.SubElement(storyline_elem, "REQUIRED_DATA")
                for data in storyline['required_data']:
                    data_obj = ET.SubElement(required_data_elem, "DATA_OBJECT")
                    for key, value in data.items():
                        if value:  # 빈 값이 아닌 경우만 XML에 추가
                            data_obj.set(key, value)
            
            if storyline['articles']:
                articles_elem = ET.SubElement(storyline_elem, "ARTICLES")
                for article in storyline['articles']:
                    article_elem = ET.SubElement(articles_elem, "ARTICLE")
                    article_elem.set("id", article['id'])
                    
                    for key, value in article['modifiers'].items():
                        if value:  # 빈 값이 아닌 경우만 XML에 추가
                            article_elem.set(key, value)
                    
                    if article['subject']:
                        subject_elem = ET.SubElement(article_elem, "SUBJECT")
                        subject_elem.text = article['subject']
                    
                    if article['text']:
                        text_elem = ET.SubElement(article_elem, "TEXT")
                        text_elem.text = article['text']
                    
                    if article['injury_description']:
                        injury_elem = ET.SubElement(article_elem, "INJURY_DESCRIPTION")
                        injury_elem.text = article['injury_description']
        
        tree = ET.ElementTree(root)
        ET.indent(tree, space="\t", level=0)
        tree.write(file_path, encoding='utf-8', xml_declaration=True)
    
    def show_help(self):
        """도움말 표시"""
        help_text = """
⚾ OOTP 스토리라인 생성기 사용법

📁 파일 작업:
• XML 파일 열기: OOTP 스토리라인 XML 파일을 로드합니다
• 저장: 편집된 스토리라인을 OOTP 호환 XML 형식으로 저장합니다

📋 스토리라인 목록:
• ID 순으로 정렬된 스토리라인 목록을 확인할 수 있습니다
• 스토리라인을 더블클릭하여 편집 화면으로 이동합니다
• 상태 아이콘으로 완성도 확인:
  ✅ 완전 설정됨 / 📝 기사 있지만 내용 부족 / ⚠️ 미완성

✏️ 기사 편집 시스템 (탭 기반):
• 📝 내용: OOTP 태그, 텍스트 작성
• ⚡ 게임 효과: 24개 modifier (사기, 능력치, 팬 관심도 등)
• 🎯 발생 조건: 71개 조건 (나이, 성적, 시기 등)
• 🏥 부상/특수: 5개 특수 효과 (부상, 은퇴, 출전정지)
• 🔧 기타: 18개 기타 설정 (시간 제한, 연결 기사 등)

🏷️ OOTP 태그 기능:
• 12개 OOTP 태그 버튼 (인물, 팀, 도시, 통계 등)
• 태그 번호 설정: 1-10 사이의 번호로 태그를 삽입
• 번호 변경: 기존 태그의 번호를 일괄 변경

🎭 여러 기사 스토리라인:
• 기사 추가/삭제로 시리즈 스토리라인 생성 가능
• 각 기사마다 독립적인 118개 속성 설정
• previous_ids로 기사 간 연결 가능

💡 팁:
• 빈 값은 자동으로 XML에서 제외됩니다
• Boolean 속성은 체크박스로 간편 설정
• 실제 OOTP XML 구조와 완벽 호환

{self.keyboard_shortcuts_help}
        """
        messagebox.showinfo("도움말", help_text)


class RequiredDataDialog:
    """참여 인물 (REQUIRED_DATA) 편집 다이얼로그"""
    
    def __init__(self, parent, title, data=None):
        self.parent = parent
        self.data = data or {}
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x500")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 다이얼로그 중앙 정렬
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"600x500+{x}+{y}")
        
        self.setup_ui()
        
        # 기존 데이터 로드
        if self.data:
            self.load_data()
    
    def setup_ui(self):
        """다이얼로그 UI 구성"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 타입 선택 프레임
        type_frame = ttk.LabelFrame(main_frame, text="참여자 타입", padding="10")
        type_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(type_frame, text="타입 선택:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        self.type_var = tk.StringVar(value=self.data.get('type', 'PLAYER'))
        type_combo = ttk.Combobox(type_frame, textvariable=self.type_var, values=DATA_OBJECT_TYPES, 
                                 state="readonly", width=20)
        type_combo.pack(anchor=tk.W, pady=5)
        type_combo.bind('<<ComboboxSelected>>', self.on_type_change)
        
        # 주인공 설정
        self.main_actor_var = tk.BooleanVar(value=self.data.get('main_actor') == '1')
        ttk.Checkbutton(type_frame, text="🎭 주인공 (main_actor)", variable=self.main_actor_var).pack(anchor=tk.W, pady=5)
        
        # 속성 설정 프레임
        attr_frame = ttk.LabelFrame(main_frame, text="속성 설정", padding="10")
        attr_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 스크롤 가능한 속성 영역
        canvas = tk.Canvas(attr_frame)
        scrollbar = ttk.Scrollbar(attr_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 속성 변수들
        self.attr_vars = {}
        
        # 초기 속성 표시
        self.update_attributes()
        
        # 버튼 프레임
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)
        
        ttk.Button(btn_frame, text="확인", command=self.ok_clicked).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="취소", command=self.cancel_clicked).pack(side=tk.RIGHT)
    
    def on_type_change(self, event=None):
        """타입 변경시 속성 업데이트"""
        self.update_attributes()
    
    def update_attributes(self):
        """선택된 타입에 따른 속성 표시"""
        # 기존 위젯들 제거
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.attr_vars.clear()
        
        # 선택된 타입에 맞는 속성들 표시
        selected_type = self.type_var.get()
        attributes = self.get_attributes_for_type(selected_type)
        
        if not attributes:
            ttk.Label(self.scrollable_frame, text="이 타입에 대한 속성이 없습니다.", 
                     font=('Arial', 10), foreground='gray').pack(pady=20)
            return
        
        # 2열로 배치
        row = 0
        col = 0
        max_cols = 2
        
        for attr in sorted(attributes):
            attr_frame = ttk.Frame(self.scrollable_frame)
            attr_frame.grid(row=row, column=col, padx=10, pady=5, sticky=(tk.W, tk.E))
            
            # 속성 라벨
            ttk.Label(attr_frame, text=f"{attr}:", font=('Arial', 9)).pack(anchor=tk.W)
            
            # 속성 값 입력
            var = tk.StringVar()
            self.attr_vars[attr] = var
            
            # JSON에서 속성 타입 결정
            attr_type = ATTR_MANAGER.get_attribute_type(attr)
            if attr_type == 'number' or attr_type == 'boolean':
                # 숫자 입력
                entry = ttk.Spinbox(attr_frame, from_=0, to=999, textvariable=var, width=15)
            else:
                # 텍스트 입력
                entry = ttk.Entry(attr_frame, textvariable=var, width=15)
            
            entry.pack(anchor=tk.W, pady=2)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # 컬럼 가중치 설정
        for i in range(max_cols):
            self.scrollable_frame.columnconfigure(i, weight=1)
    
    def get_attributes_for_type(self, obj_type):
        """타입별 사용 가능한 속성들 반환 - JSON에서 동적 로드"""
        return ATTR_MANAGER.get_attributes_for_type(obj_type)
    
    def load_data(self):
        """기존 데이터 로드"""
        for key, value in self.data.items():
            if key == 'type':
                self.type_var.set(value)
            elif key == 'main_actor':
                self.main_actor_var.set(value == '1')
            elif key in self.attr_vars:
                self.attr_vars[key].set(value)
    
    def ok_clicked(self):
        """확인 버튼 클릭"""
        result = {
            'type': self.type_var.get()
        }
        
        # 주인공 설정
        if self.main_actor_var.get():
            result['main_actor'] = '1'
        
        # 속성 값들 수집 (빈 값 제외)
        for attr, var in self.attr_vars.items():
            value = var.get().strip()
            if value:
                result[attr] = value
        
        self.result = result
        self.dialog.destroy()
    
    def cancel_clicked(self):
        """취소 버튼 클릭"""
        self.result = None
        self.dialog.destroy()
    
    def show(self):
        """다이얼로그 표시 및 결과 반환"""
        self.dialog.wait_window()
        return self.result


def main():
    root = tk.Tk()
    app = ModernOOTPStorylineGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 