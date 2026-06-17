import { useEffect, useState } from 'react';
import { Doc, DocCollection } from '@blocksuite/store';

interface HeaderProps {
  collection: DocCollection;
  doc: Doc | null;
  mode: 'page' | 'edgeless';
  onChangeMode: (mode: 'page' | 'edgeless') => void;
  onLoadDemo: () => void;
  onClearDoc: () => void;
}

export function Header({
  collection,
  doc,
  mode,
  onChangeMode,
  onLoadDemo,
  onClearDoc,
}: HeaderProps) {
  const [title, setTitle] = useState('');
  const [stats, setStats] = useState({ blocks: 0, characters: 0, words: 0 });

  // Sync title and subscribe to statistics changes when active document changes
  useEffect(() => {
    if (!doc) {
      setTitle('');
      setStats({ blocks: 0, characters: 0, words: 0 });
      return;
    }

    // Get current title from metadata
    const meta = collection.meta.getDocMeta(doc.id);
    setTitle(meta?.title || 'Untitled');

    // Calculate initial statistics
    const updateStats = () => {
      const blocks = doc.getBlocks();
      let characters = 0;
      let words = 0;

      blocks.forEach((block) => {
        // Check if block has a text property (standard for text blocks in BlockSuite)
        const textProp = block.text;
        if (textProp && typeof textProp.toString === 'function') {
          const content = textProp.toString();
          characters += content.length;
          
          const cleanText = content.trim();
          if (cleanText) {
            words += cleanText.split(/\s+/).length;
          }
        }
      });

      setStats({
        blocks: blocks.length,
        characters,
        words,
      });
    };

    updateStats();

    // Listen to block updates inside this doc to update live statistics
    const blockUpdateSub = doc.slots.blockUpdated.on(() => {
      updateStats();
    });

    // Listen for external title updates
    const metaUpdateSub = collection.meta.docMetaUpdated.on(() => {
      const currentMeta = collection.meta.getDocMeta(doc.id);
      if (currentMeta && currentMeta.title !== title) {
        setTitle(currentMeta.title || 'Untitled');
      }
    });

    return () => {
      blockUpdateSub.dispose();
      metaUpdateSub.dispose();
    };
  }, [doc, collection]);

  // Handle title edit changes
  const handleTitleChange = (newTitle: string) => {
    setTitle(newTitle);
    if (!doc) return;

    // 1. Update document collection metadata for sidebar listing
    collection.meta.setDocMeta(doc.id, { title: newTitle });

    // 2. Synchronize title into the editor's root page block title if it exists
    const rootPage = doc.root as any;
    if (rootPage && rootPage.title) {
      const rootTitle = rootPage.title;
      try {
        doc.transact(() => {
          rootTitle.clear();
          rootTitle.insert(newTitle, 0);
        });
      } catch (e) {
        console.error('Failed to sync title into root page block:', e);
      }
    }
  };

  return (
    <header className="header">
      <div className="header-left">
        {doc ? (
          <input
            type="text"
            className="header-title-input"
            value={title}
            onChange={(e) => handleTitleChange(e.target.value)}
            placeholder="Untitled Document"
            title="Edit Document Title"
          />
        ) : (
          <span className="header-title-input" style={{ opacity: 0.5, cursor: 'default' }}>
            No Document Selected
          </span>
        )}
      </div>

      <div className="header-right">
        {doc && (
          <>
            {/* Statistics Dashboard */}
            <div className="stats-panel" title="Live Document Statistics">
              <div className="stat-item">
                <span>Blocks:</span>
                <span className="stat-value">{stats.blocks}</span>
              </div>
              <div style={{ width: '1px', height: '12px', background: 'var(--border)' }}></div>
              <div className="stat-item">
                <span>Words:</span>
                <span className="stat-value">{stats.words}</span>
              </div>
              <div style={{ width: '1px', height: '12px', background: 'var(--border)' }}></div>
              <div className="stat-item">
                <span>Chars:</span>
                <span className="stat-value">{stats.characters}</span>
              </div>
            </div>

            {/* Layout Mode Toggler */}
            <div className="mode-toggle">
              <button
                className={`mode-btn ${mode === 'page' ? 'active' : ''}`}
                onClick={() => onChangeMode('page')}
                title="Switch to Page Layout"
              >
                <span>📄</span>
                Page
              </button>
              <button
                className={`mode-btn ${mode === 'edgeless' ? 'active' : ''}`}
                onClick={() => onChangeMode('edgeless')}
                title="Switch to Edgeless Canvas"
              >
                <span>🎨</span>
                Edgeless
              </button>
            </div>

            {/* Quick action buttons */}
            <div className="action-buttons">
              <button
                className="btn-action primary"
                onClick={onLoadDemo}
                title="Insert demo headings, lists, and code blocks"
              >
                ✨ Load Demo Content
              </button>
              <button
                className="btn-action"
                onClick={onClearDoc}
                title="Clear all page content blocks"
              >
                🗑️ Clear
              </button>
            </div>
          </>
        )}
      </div>
    </header>
  );
}
