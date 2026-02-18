odoo.define('modulo.A2UIDashboard', function(require) {
    'use strict';
    
    const { useEffect, useState } = owl;
    const { Component } = owl;

    class A2UIDashboard extends Component {
        setup() {
            const props = this.props;
            this.dashboard = JSON.parse(props.data || '{}');
            this.renderDashboard();
        }

        renderDashboard() {
            const type = this.dashboard.type;
            
            if (type === 'table') {
                return this.renderTable();
            } else if (type === 'summary_cards') {
                return this.renderSummaryCards();
            } else if (type === 'pipeline') {
                return this.renderPipeline();
            } else if (type === 'opportunities') {
                return this.renderOpportunities();
            } else if (type === 'alert_table') {
                return this.renderAlertTable();
            } else if (type === 'help_menu') {
                return this.renderHelpMenu();
            }
        }

        renderTable() {
            const data = this.dashboard;
            return `
                <div class="a2ui-table-container">
                    <h3>${data.title}</h3>
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                ${data.columns.map(col => `<th>${col.label}</th>`).join('')}
                            </tr>
                        </thead>
                        <tbody>
                            ${data.rows.map(row => `
                                <tr>
                                    ${data.columns.map(col => `<td>${row[col.key]}</td>`).join('')}
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        }

        renderSummaryCards() {
            return `
                <div class="a2ui-cards-container">
                    ${this.dashboard.cards.map(card => `
                        <div class="a2ui-card bg-${card.color}">
                            <div class="card-icon">${card.icon}</div>
                            <div class="card-title">${card.title}</div>
                            <div class="card-value">${card.value}</div>
                            ${card.subtitle ? `<div class="card-subtitle">${card.subtitle}</div>` : ''}
                        </div>
                    `).join('')}
                </div>
            `;
        }

        renderHelpMenu() {
            const data = this.dashboard;
            return `
                <div class="a2ui-help-menu">
                    <div class="help-options">
                        ${data.options.map(option => `
                            <div class="help-option-card">
                                <div class="option-icon">${option.icon}</div>
                                <div class="option-title">${option.title}</div>
                                <div class="option-description">${option.description}</div>
                                <div class="option-keywords">
                                    ${option.keywords.map(kw => `<span class="keyword">${kw}</span>`).join('')}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                    <div class="help-message">
                        ${data.message}
                    </div>
                </div>
            `;
        }
    }

    return A2UIDashboard;
});