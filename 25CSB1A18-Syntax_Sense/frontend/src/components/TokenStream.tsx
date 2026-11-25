import React, { useState, useMemo } from 'react';
import type { LexicalToken } from '../types';
import './TokenStream.css';

export interface TokenStreamProps {
  tokens?: LexicalToken[];
  language?: string;
}

export const TokenStream: React.FC<TokenStreamProps> = ({ tokens, language }) => {
  const [filterQuery, setFilterQuery] = useState('');

  const tokenList = tokens || [];

  const filteredTokens = useMemo(() => {
    if (!filterQuery.trim()) return tokenList;
    const q = filterQuery.toLowerCase();
    return tokenList.filter(
      (tok) =>
        tok.type.toLowerCase().includes(q) ||
        tok.value.toLowerCase().includes(q) ||
        String(tok.line).includes(q) ||
        String(tok.column).includes(q)
    );
  }, [tokenList, filterQuery]);

  const renderTokenValue = (val: string) => {
    if (val === '\n') {
      return <span className="token-special-char">\n</span>;
    }
    if (val === '\r\n') {
      return <span className="token-special-char">\r\n</span>;
    }
    if (val === '\t') {
      return <span className="token-special-char">\t</span>;
    }
    if (val.trim() === '' && val.length > 0) {
      return <span className="token-special-char">{`[space x${val.length}]`}</span>;
    }
    return val;
  };

  const getTokenTypeBadgeClass = (type: string) => {
    const upper = type.toUpperCase();
    if (upper.includes('KEYWORD')) return 'token-badge-keyword';
    if (upper.includes('IDENTIFIER') || upper.includes('NAME')) return 'token-badge-identifier';
    if (upper.includes('LITERAL') || upper.includes('NUMBER') || upper.includes('STRING')) return 'token-badge-literal';
    if (upper.includes('OPERATOR') || upper.includes('OP')) return 'token-badge-operator';
    if (upper.includes('DELIMITER') || upper.includes('PUNCTUATION') || upper.includes('SEMICOLON') || upper.includes('BRACE')) return 'token-badge-delimiter';
    if (upper.includes('COMMENT')) return 'token-badge-comment';
    return 'token-badge-default';
  };

  if (!tokens || tokens.length === 0) {
    return (
      <div className="token-stream-panel">
        <div className="token-stream-header">
          <h3 className="token-stream-title">Lexical Analysis – Token Stream</h3>
        </div>
        <div className="token-stream-empty">
          <span className="empty-icon">🔤</span>
          <p className="empty-text">No lexical tokens generated</p>
          <p className="empty-subtext">
            The lexical analyzer did not return any tokens for this code input.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="token-stream-panel">
      <div className="token-stream-header">
        <div className="token-stream-title-wrap">
          <h3 className="token-stream-title">Lexical Analysis – Token Stream</h3>
          <span className="token-stream-subtitle">
            {language ? `${language.toUpperCase()} Lexer Output` : 'Lexer Output'}
          </span>
        </div>
        <div className="token-stream-badge-wrap">
          <span className="tokens-count">
            {tokenList.length} {tokenList.length === 1 ? 'token' : 'tokens'}
          </span>
        </div>
      </div>

      <div className="token-stream-toolbar">
        <input
          type="text"
          className="token-filter-input"
          placeholder="Filter tokens by type, value, line..."
          value={filterQuery}
          onChange={(e) => setFilterQuery(e.target.value)}
        />
        {filterQuery && (
          <span className="token-filter-count">
            Showing {filteredTokens.length} of {tokenList.length}
          </span>
        )}
      </div>

      <div className="token-table-container">
        <table className="token-stream-table">
          <thead>
            <tr>
              <th className="col-index">#</th>
              <th className="col-type">Token Type</th>
              <th className="col-value">Token Value</th>
              <th className="col-line">Line</th>
              <th className="col-col">Column</th>
            </tr>
          </thead>
          <tbody>
            {filteredTokens.length === 0 ? (
              <tr>
                <td colSpan={5} className="no-matches">
                  No tokens matching "{filterQuery}"
                </td>
              </tr>
            ) : (
              filteredTokens.map((token, index) => (
                <tr key={`${token.line}-${token.column}-${index}`}>
                  <td className="col-index">{index + 1}</td>
                  <td className="col-type">
                    <span className={`token-type-badge ${getTokenTypeBadgeClass(token.type)}`}>
                      {token.type}
                    </span>
                  </td>
                  <td className="col-value">
                    <code className="token-value-code">{renderTokenValue(token.value)}</code>
                  </td>
                  <td className="col-line">{token.line}</td>
                  <td className="col-col">{token.column}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default TokenStream;
