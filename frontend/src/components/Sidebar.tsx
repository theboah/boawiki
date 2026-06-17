import { useEffect, useState } from 'react';
import { DocCollection } from '@blocksuite/store';
import type { DocMeta } from '@blocksuite/store';

interface SidebarProps {
  collection: DocCollection;
  activeDocId: string | null;
  onSelectDoc: (id: string) => void;
  onCreateDoc: () => void;
  onDeleteDoc: (id: string) => void;
}

export function Sidebar({
  collection,
  activeDocId,
  onSelectDoc,
  onCreateDoc,
  onDeleteDoc,
}: SidebarProps) {
  const [docMetas, setDocMetas] = useState<DocMeta[]>([]);

  useEffect(() => {
    // Initial fetch of doc metadata
    setDocMetas([...collection.meta.docMetas]);

    // Register listener for document metadata modifications (e.g. creations, deletions, title changes)
    const disposable = collection.meta.docMetaUpdated.on(() => {
      setDocMetas([...collection.meta.docMetas]);
    });

    return () => {
      disposable.dispose();
    };
  }, [collection]);

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">B</div>
        <span className="sidebar-title">BoaWiki</span>
      </div>
      
      <div className="sidebar-actions">
        <button className="btn-new-doc" onClick={onCreateDoc} title="Create a new document">
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M5 12h14" />
            <path d="M12 5v14" />
          </svg>
          New Document
        </button>
      </div>

      <div className="doc-list-container">
        {docMetas.map((doc) => (
          <div
            key={doc.id}
            className={`doc-item ${activeDocId === doc.id ? 'active' : ''}`}
            onClick={() => onSelectDoc(doc.id)}
            title={`Open: ${doc.title || 'Untitled'}`}
          >
            <div className="doc-info">
              <span className="doc-icon">📄</span>
              <span className="doc-title-text">
                {doc.title || 'Untitled'}
              </span>
            </div>
            
            <button
              className="btn-delete-doc"
              title="Delete Document"
              onClick={(e) => {
                e.stopPropagation();
                if (confirm(`Are you sure you want to delete "${doc.title || 'Untitled'}"?`)) {
                  onDeleteDoc(doc.id);
                }
              }}
            >
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M3 6h18" />
                <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" />
                <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
              </svg>
            </button>
          </div>
        ))}

        {docMetas.length === 0 && (
          <div style={{ padding: '24px 16px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px' }}>
            No documents yet. Click "New Document" to get started!
          </div>
        )}
      </div>
    </aside>
  );
}
