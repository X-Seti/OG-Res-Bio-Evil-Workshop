#this belongs in apps/components/research_tab.py - Version: 1
# X-Seti - February18 2025 - ResBio-Evil-Workshop 1.0 - Research Tab Component
"""
Research Tab - GUI for managing research database entries.
Left: Category tree, Right: Markdown editor with search/filter.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QTextEdit, QLineEdit, QPushButton, QMessageBox, QInputDialog,
    QComboBox, QLabel, QDialog, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QFont

# Import research database - handles both locations
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    # Try apps.core import (preferred)
    from apps.core.research_db import ResearchDB
except ImportError:
    try:
        # Fallback to local import
        from research_db import ResearchDB
    except ImportError as e:
        print(f"CRITICAL: Cannot import ResearchDB: {e}")
        raise

##Methods list -
# __init__
# _setup_ui
# _setup_left_panel
# _setup_right_panel
# _populate_tree
# _on_tree_item_selected
# _on_add_entry
# _on_edit_entry
# _on_delete_entry
# _on_search
# _on_export
# _on_tag_filter
# _refresh_tree
# _create_entry_dialog

##class ResearchTab: -

class ResearchTab(QWidget): #vers 1
    """Research database tab for file format findings"""
    
    entry_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None): #vers 1
        super().__init__(parent)
        self.db = ResearchDB()
        self.current_entry = None
        self._setup_ui()
    
    def _setup_ui(self): #vers 1
        """Setup main UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        self._setup_left_panel(layout)
        self._setup_right_panel(layout)
        
        self.setLayout(layout)
        self._populate_tree()
        self._refresh_tag_combo()
    
    def _setup_left_panel(self, parent_layout: QHBoxLayout): #vers 1
        """Setup left panel with category tree"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Title
        title = QLabel("Categories")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(10)
        title.setFont(title_font)
        left_layout.addWidget(title)
        
        # Category tree
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Research Topics")
        self.tree.itemSelectionChanged.connect(self._on_tree_item_selected)
        left_layout.addWidget(self.tree)
        
        # Action buttons
        button_layout = QVBoxLayout()
        
        self.add_btn = QPushButton("Add Entry")
        self.add_btn.clicked.connect(self._on_add_entry)
        button_layout.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton("Edit Entry")
        self.edit_btn.clicked.connect(self._on_edit_entry)
        self.edit_btn.setEnabled(False)
        button_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("Delete Entry")
        self.delete_btn.clicked.connect(self._on_delete_entry)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)
        
        left_layout.addLayout(button_layout)
        
        # Set width
        left_widget.setMaximumWidth(250)
        parent_layout.addWidget(left_widget)
    
    def _setup_right_panel(self, parent_layout: QHBoxLayout): #vers 1
        """Setup right panel with editor and search"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search title/content...")
        self.search_input.textChanged.connect(self._on_search)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        right_layout.addLayout(search_layout)
        
        # Tag filter
        tag_layout = QHBoxLayout()
        tag_label = QLabel("Filter by Tag:")
        self.tag_combo = QComboBox()
        self.tag_combo.addItem("All Tags")
        self.tag_combo.currentTextChanged.connect(self._on_tag_filter)
        tag_layout.addWidget(tag_label)
        tag_layout.addWidget(self.tag_combo)
        tag_layout.addStretch()
        right_layout.addLayout(tag_layout)
        
        # Entry title (read-only)
        self.entry_title = QLineEdit()
        self.entry_title.setReadOnly(True)
        self.entry_title.setPlaceholderText("Select an entry...")
        right_layout.addWidget(self.entry_title)
        
        # Text editor
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Entry content (Markdown supported)...")
        self.editor.setMinimumHeight(300)
        right_layout.addWidget(self.editor)
        
        # Export button
        export_btn = QPushButton("Export All to Markdown")
        export_btn.clicked.connect(self._on_export)
        right_layout.addWidget(export_btn)
        
        parent_layout.addWidget(right_widget, 1)
    
    def _populate_tree(self, search_query: str = "", tag_filter: str = ""): #vers 1
        """Populate tree with categories and entries"""
        self.tree.clear()
        
        for category in self.db.get_categories():
            cat_item = QTreeWidgetItem(self.tree)
            cat_item.setText(0, category)
            cat_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "category"})
            
            # Get entries for category
            entries = self.db.get_entries_by_category(category)
            
            # Apply search filter
            if search_query:
                entries = [e for e in entries if search_query.lower() in e["title"].lower()]
            
            # Apply tag filter
            if tag_filter and tag_filter != "All Tags":
                entries = [e for e in entries if tag_filter in e.get("tags", [])]
            
            # Add entries
            for entry in entries:
                entry_item = QTreeWidgetItem(cat_item)
                entry_item.setText(0, entry["title"])
                entry_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "entry", "id": entry["id"]})
    
    def _on_tree_item_selected(self): #vers 1
        """Handle tree item selection"""
        item = self.tree.currentItem()
        if not item:
            self.editor.clear()
            self.entry_title.clear()
            self.current_entry = None
            self.edit_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            return
        
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data or data.get("type") != "entry":
            self.editor.clear()
            self.edit_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            return
        
        entry_id = data.get("id")
        entry = self.db.get_entry(entry_id)
        
        if entry:
            self.current_entry = entry
            self.entry_title.setText(f"{entry['title']} ({entry['category']})")
            self.editor.setText(entry["content"])
            self.edit_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)
    
    def _on_add_entry(self): #vers 1
        """Show dialog to add new entry"""
        dialog = QInputDialog(self)
        dialog.setWindowTitle("Add Research Entry")
        
        title, ok = QInputDialog.getText(self, "Add Entry", "Title:")
        if not ok or not title:
            return
        
        # Category selection
        categories = self.db.get_categories()
        category, ok = QInputDialog.getItem(
            self, "Select Category", "Category:",
            categories, 0, False
        )
        if not ok:
            return
        
        content, ok = QInputDialog.getMultiLineText(
            self, "Add Entry", "Content (Markdown):"
        )
        if not ok:
            return
        
        # Tag selection
        all_tags = self.db.DEFAULT_TAGS + self.db.get_all_tags()
        all_tags = sorted(list(set(all_tags)))
        
        tags_text, ok = QInputDialog.getItem(
            self, "Select Tags", "Tags (comma separated):",
            all_tags, 0, False
        )
        if not ok:
            return
        
        tags = [t.strip() for t in tags_text.split(",") if t.strip()]
        
        if self.db.add_entry(title, category, content, tags):
            self._refresh_tree()
            QMessageBox.information(self, "Success", "Entry added successfully!")
        else:
            QMessageBox.critical(self, "Error", "Failed to add entry")
    
    def _on_edit_entry(self): #vers 1
        """Edit current entry"""
        if not self.current_entry:
            QMessageBox.warning(self, "No Selection", "Please select an entry to edit")
            return
        
        new_content = self.editor.toPlainText()
        if self.db.edit_entry(self.current_entry["id"], content=new_content):
            self._refresh_tree()
            QMessageBox.information(self, "Success", "Entry updated!")
        else:
            QMessageBox.critical(self, "Error", "Failed to update entry")
    
    def _on_delete_entry(self): #vers 1
        """Delete current entry"""
        if not self.current_entry:
            return
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete '{self.current_entry['title']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.db.delete_entry(self.current_entry["id"]):
                self._refresh_tree()
                self.editor.clear()
                self.entry_title.clear()
                QMessageBox.information(self, "Success", "Entry deleted!")
            else:
                QMessageBox.critical(self, "Error", "Failed to delete entry")
    
    def _on_search(self, query: str): #vers 1
        """Handle search text change"""
        tag_filter = "" if self.tag_combo.currentText() == "All Tags" else self.tag_combo.currentText()
        self._populate_tree(query, tag_filter)
    
    def _on_tag_filter(self, tag: str): #vers 1
        """Handle tag filter change"""
        search_query = self.search_input.text()
        tag_filter = "" if tag == "All Tags" else tag
        self._populate_tree(search_query, tag_filter)
    
    def _on_export(self): #vers 1
        """Export all entries to markdown"""
        if self.db.export_to_markdown():
            QMessageBox.information(
                self, "Success",
                "Research database exported to research_export.md"
            )
        else:
            QMessageBox.critical(self, "Error", "Failed to export database")
    
    def _refresh_tree(self): #vers 1
        """Refresh tree with current filters"""
        search_query = self.search_input.text()
        tag_filter = "" if self.tag_combo.currentText() == "All Tags" else self.tag_combo.currentText()
        self._populate_tree(search_query, tag_filter)
        
        # Update tag combo
        self._refresh_tag_combo()
        
        self.current_entry = None
        self.editor.clear()
        self.entry_title.clear()
        self.edit_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
    
    def _refresh_tag_combo(self): #vers 1
        """Refresh tag combo with all tags from database"""
        all_tags = self.db.get_all_tags()
        self.tag_combo.blockSignals(True)
        current = self.tag_combo.currentText()
        self.tag_combo.clear()
        self.tag_combo.addItem("All Tags")
        for tag in sorted(all_tags):
            self.tag_combo.addItem(tag)
        if current in [self.tag_combo.itemText(i) for i in range(self.tag_combo.count())]:
            self.tag_combo.setCurrentText(current)
        self.tag_combo.blockSignals(False)
    
    def load_database(self): #vers 1
        """Load and display database"""
        self._refresh_tree()
        self._populate_tree()
