"use client";

import React, { useRef, useState, useEffect } from "react";
import ContentEditable, { ContentEditableEvent } from "react-contenteditable";

interface PromptEditorProps {
  value: string;
  onChange: (value: string) => void;
  availableTags: string[];
  disabled?: boolean;
}

// Ensure the dataset context ID tag is universally known
export const DATASET_CONTEXT_ID = "question_task";

export function PromptEditor({
  value,
  onChange,
  availableTags,
  disabled = false,
}: PromptEditorProps) {
  const contentEditableRef = useRef<HTMLElement>(null);

  // Converts backend template text (e.g. "Hello {{task_id}}") to HTML with pill tags.
  const textToHtml = (text: string) => {
    if (!text) return "";
    let html = text.replace(/</g, "&lt;").replace(/>/g, "&gt;");
    html = html.replace(/\{\{(.*?)\}\}/g, (match, id) => {
      // Create a standard inline span with minimal styling so it behaves mostly like text for layout.
      // We prepend and append a zero-width space (&#8203;) to ensure the browser can correctly position the cursor 
      // next to the contenteditable="false" element, which fixes backspace deletion bugs.
      return `&#8203;<span class="bg-blue-100 text-blue-700 px-1 mx-0.5 rounded border border-blue-200 select-none cursor-default" contenteditable="false" data-tag-id="${id}">#${id}</span>&#8203;`;
    });
    // Replace newlines with <br> so contenteditable maintains line breaks correctly.
    return html.replace(/\n/g, "<br>");
  };

  // Recursively extract text from DOM nodes, replacing pills with {{id}} and block tags with newlines.
  const extractText = (node: Node): string => {
    if (node.nodeType === Node.TEXT_NODE) {
      // ContentEditable uses &nbsp; (\xA0) to preserve multiple spaces. Convert back to plain space.
      // Also strip zero-width spaces (\u200B) manually inserted around tags for cursor stability.
      return (node.textContent || "").replace(/\u00A0/g, " ").replace(/\u200B/g, "");
    }
    
    if (node.nodeType === Node.ELEMENT_NODE) {
      const el = node as HTMLElement;
      
      // If it's our special tag, return the template string
      if (el.tagName === "SPAN" && el.hasAttribute("data-tag-id")) {
        return `{{${el.getAttribute("data-tag-id")}}}`;
      }
      
      if (el.tagName === "BR") {
        return "\n";
      }
      
      // Blocks implicitly add newlines for contentEditable.
      const isBlock = el.tagName === "DIV" || el.tagName === "P";
      let text = isBlock && node.previousSibling ? "\n" : "";

      for (let i = 0; i < node.childNodes.length; i++) {
        text += extractText(node.childNodes[i]);
      }
      
      return text;
    }
    return "";
  };

  const htmlToText = (rawHtml: string) => {
    const temp = document.createElement("div");
    temp.innerHTML = rawHtml;
    // Strip trailing zero-width space or newlines that ContentEditable sometimes appends unnecessarily
    let text = extractText(temp);
    // If text ends with newline because of a trailing <br>, remove it to avoid endless trailing newline issues
    if (text.endsWith("\n") && rawHtml.endsWith("<br>")) {
      text = text.slice(0, -1);
    }
    return text;
  };

  // State to hold the HTML representation
  const [html, setHtml] = useState<string>(() => textToHtml(value));

  // Sync from props (if external value changed non-interactively like clicking "Insert Tag" or loading Recipe)
  useEffect(() => {
    const currentText = htmlToText(html);
    if (value !== currentText) {
      setHtml(textToHtml(value));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [value]);

  const handleChange = (e: ContentEditableEvent) => {
    const newHtml = e.target.value;
    setHtml(newHtml);
    const newText = htmlToText(newHtml);
    onChange(newText);
  };

  const handleInsertTag = (e: React.MouseEvent, tagId: string) => {
    e.preventDefault(); // Prevent losing focus on editor when mousedown fires
    if (disabled) return;
    
    const editor = contentEditableRef.current;
    if (!editor) return;

    // We generate the raw HTML representation of the tag wrapper
    const tagHtml = `&#8203;<span class="bg-blue-100 text-blue-700 px-1 mx-0.5 rounded border border-blue-200 select-none cursor-default" contenteditable="false" data-tag-id="${tagId}">#${tagId}</span>&#8203;`;

    // Attempt to insert at current cursor via execCommand
    editor.focus();
    let commandSuccess = false;
    try {
      commandSuccess = document.execCommand("insertHTML", false, tagHtml);
    } catch (e) {
      console.warn("execCommand not supported", e);
    }

    if (!commandSuccess) {
      // Fallback: append at the end
      const spacer = value && !value.endsWith(" ") && !value.endsWith("\\n") ? " " : "";
      const newText = value + spacer + `{{${tagId}}}`;
      onChange(newText);
    } else {
      // Sync State explicitly so react-contenteditable triggers an onChange
      const newInnerHtml = editor.innerHTML;
      setHtml(newInnerHtml);
      const newText = htmlToText(newInnerHtml);
      onChange(newText);
    }
  };

  return (
    <div className="flex flex-col gap-3 w-full border border-gray-200 rounded-lg p-3 bg-gray-50">
      {/* Editor Area */}
      <ContentEditable
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        innerRef={contentEditableRef as any}
        html={html}
        disabled={disabled}
        onChange={handleChange}
        className="w-full text-sm font-sans focus:outline-none focus:ring-1 focus:ring-blue-400 bg-white border border-gray-200 rounded px-3 py-2 min-h-[120px] shadow-inner"
      />
      
      {/* Tag Selection Dropdown inline below the editor */}
      <div className="flex bg-gray-100 p-2 rounded-md border border-gray-200 shadow-sm mt-1">
        <select
          disabled={disabled || availableTags.length === 0}
          onChange={(e: React.ChangeEvent<HTMLSelectElement>) => {
            if (e.target.value) {
              handleInsertTag(e as unknown as React.MouseEvent<HTMLButtonElement>, e.target.value);
              e.target.value = ""; // Reset after selection
            }
          }}
          className="text-xs w-full bg-white border border-gray-300 rounded px-2 py-1.5 focus:outline-none focus:border-blue-400 disabled:opacity-50"
          defaultValue=""
        >
          <option value="" disabled>
            {availableTags.length === 0 ? "No variables available" : "-- Select a variable to insert --"}
          </option>
          {availableTags.map((tag) => {
            const isDataset = tag === DATASET_CONTEXT_ID;
            return (
              <option key={tag} value={tag}>
                {isDataset ? `Original Dataset Question (#${tag})` : `Task Output (#${tag})`}
              </option>
            );
          })}
        </select>
      </div>
    </div>
  );
}

