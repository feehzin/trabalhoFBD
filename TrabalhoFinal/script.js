
document.addEventListener('DOMContentLoaded', () => {

    const API_BASE_URL = 'http://127.0.0.1:8000';

    const homeSection = document.getElementById('home-section');
    const menuCards = document.querySelectorAll('.menu-card');
    const contentSections = document.querySelectorAll('.content-section:not(#home-section)');
    const backToHomeButtons = document.querySelectorAll('.back-to-home-btn');

    const showSection = (targetId) => {
        contentSections.forEach(section => {
            section.classList.remove('active');
        });
        homeSection.classList.remove('active');

        const targetSection = document.getElementById(targetId);
        if (targetSection) {
            targetSection.classList.add('active');
            if (targetId === 'agendamentos-section') {
                loadAgendamentos();
            } else if (targetId === 'consultas-section') {
                loadConsultas();
            } else if (targetId === 'medicos-section') {
                loadMedicos();
            } else if (targetId === 'pacientes-section') {
                loadPacientes();
            } else if (targetId === 'remarcas-section') {
                loadRemarcas();
            } else if (targetId === 'relatorios-section') {
                loadReports();
            }
        }
    };

    menuCards.forEach(card => {
        card.addEventListener('click', (event) => {
            const targetId = event.currentTarget.getAttribute('data-target');
            showSection(targetId);
        });
    });

    backToHomeButtons.forEach(button => {
        button.addEventListener('click', () => {
            contentSections.forEach(section => section.classList.remove('active'));
            homeSection.classList.add('active');
        });
    });


    const apiFetch = async (url, options = {}) => {
        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `Erro HTTP: ${response.status}`);
            }
            return response.status !== 204 ? await response.json() : null;
        } catch (error) {
            console.error('Erro na API:', error);
            alert(`Erro na API: ${error.message}`);
            throw error;
        }
    };

    const agendamentosTbody = document.getElementById('agendamentos-tbody');
    const agendamentoForm = document.getElementById('agendamento-form');

    const renderAgendamentos = (agendamentos) => {
        agendamentosTbody.innerHTML = '';
        if (agendamentos.length === 0) {
            agendamentosTbody.innerHTML = '<tr><td colspan="5">Nenhum agendamento encontrado.</td></tr>';
            return;
        }
        agendamentos.forEach(ag => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${ag.id_agendamento}</td>
                <td>${ag.id_paciente}</td>
                <td>${new Date(ag.data).toLocaleString('pt-BR')}</td>
                <td>${ag.status}</td>
                <td class="action-buttons">
                    <button class="edit-btn" onclick="setupEditForm('agendamento', ${ag.id_agendamento}, ${ag.id_paciente})">Editar</button>
                    <button class="delete-btn" onclick="deleteItem('agendamento', '${ag.id_agendamento}|${ag.id_paciente}')">Cancelar</button>
                </td>
            `;
            agendamentosTbody.appendChild(tr);
        });
    };

    const loadAgendamentos = () => apiFetch(`${API_BASE_URL}/agendamentos`).then(renderAgendamentos);

    agendamentoForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const idAgendamento = document.getElementById('agendamento_id').value;
        const idPaciente = document.getElementById('ag_id_paciente').value;

        const method = idAgendamento ? 'PATCH' : 'POST';
        let url = `${API_BASE_URL}/agendamentos`;
        if (idAgendamento) {
            url = `${API_BASE_URL}/agendamentos/${idAgendamento}/${idPaciente}`;
        }

        const body = {
            id_paciente: parseInt(idPaciente),
            data: new Date(document.getElementById('ag_data_hora').value).toISOString(),
            observacoes: document.getElementById('ag_observacoes').value,
        };

        if (idAgendamento) {
            body.status = document.getElementById('ag_status').value;
        }

        await apiFetch(url, { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
        resetForm('agendamento');
        loadAgendamentos();
    });

    const consultasTbody = document.getElementById('consultas-tbody');
    const consultaForm = document.getElementById('consulta-form');

    const renderConsultas = (consultas) => {
        consultasTbody.innerHTML = '';
        if (consultas.length === 0) {
            consultasTbody.innerHTML = '<tr><td colspan="6">Nenhuma consulta encontrada.</td></tr>';
            return;
        }
        consultas.forEach(c => {
            const dataHora = c.data_hora
                ? new Date(c.data_hora).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })
                : 'N/A';
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${c.id_agendamento}</td>
                <td>${c.crm}</td>
                <td>${c.id_paciente}</td>
                <td>${dataHora}</td>
                <td>${c.diagnostico || 'N/A'}</td>
                <td class="action-buttons">
                    <button class="edit-btn" onclick="setupEditForm('consulta', '${c.crm}|${c.id_agendamento}|${c.id_paciente}')">Editar</button>
                    <button class="delete-btn" onclick="deleteItem('consulta', '${c.crm}|${c.id_agendamento}|${c.id_paciente}')">Deletar</button>
                </td>
            `;
            consultasTbody.appendChild(tr);
        });
    };

    const loadConsultas = () => apiFetch(`${API_BASE_URL}/consultas`).then(renderConsultas);

    consultaForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const crm = document.getElementById('con_crm').value;
        const id_agendamento = parseInt(document.getElementById('con_id_agendamento').value);
        const id_paciente = parseInt(document.getElementById('con_id_paciente').value);

        const isEditing = document.getElementById('consulta_id').value === 'editing';

        const method = isEditing ? 'PATCH' : 'POST';
        const url = isEditing ? `${API_BASE_URL}/consultas/${crm}/${id_agendamento}/${id_paciente}` : `${API_BASE_URL}/consultas`;

        const body = {
            diagnostico: document.getElementById('con_diagnostico').value,
            observacoes: document.getElementById('con_observacoes').value
        };

        if (!isEditing) {
            body.crm = crm;
            body.id_agendamento = id_agendamento;
            body.id_paciente = id_paciente;
            body.data_hora = new Date(document.getElementById('con_data_hora').value).toISOString();
        }

        await apiFetch(url, { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
        resetForm('consulta');
        loadConsultas();
    });

    const encaminhamentoForm = document.getElementById('encaminhamento-form');
    const encTipoSelect = document.getElementById('enc_tipo');

    encTipoSelect.addEventListener('change', () => {
        const tipo = encTipoSelect.value;
        document.getElementById('enc-exames-group').style.display = tipo === 'Exame' || tipo === 'Ambos' ? 'block' : 'none';
        document.getElementById('enc-agendamento-group').style.display = tipo === 'Consulta' || tipo === 'Ambos' ? 'block' : 'none';
    });

    encaminhamentoForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const tipo = document.getElementById('enc_tipo').value;
        const id_agendamento_origem = parseInt(document.getElementById('enc_id_consulta').value);
        const id_paciente_origem = parseInt(document.getElementById('enc_id_paciente_origem').value);

        const body = {
            id_agendamento: id_agendamento_origem,
            id_paciente: id_paciente_origem,
            tipo: tipo,
            observacoes: document.getElementById('enc_observacoes').value
        };

        if (tipo === 'Exame' || tipo === 'Ambos') {
            const examesIds = document.getElementById('enc_exames_ids').value;
            if (examesIds) body.exames_ids = examesIds.split(',').map(id => parseInt(id.trim()));
            else if (tipo === 'Exame' || tipo === 'Ambos') {
                alert("Para encaminhamento de Exame ou Ambos, 'IDs dos Exames' é obrigatório.");
                return;
            }
        }
        if (tipo === 'Consulta' || tipo === 'Ambos') {
            const agendamentoNovoId = document.getElementById('enc_novo_agendamento_id').value;
            const pacienteNovoId = document.getElementById('enc_novo_paciente_id').value;
            if (agendamentoNovoId && pacienteNovoId) {
                body.agendamento_novo_id = parseInt(agendamentoNovoId);
                body.paciente_novo_id = parseInt(pacienteNovoId);
            } else if (tipo === 'Consulta' || tipo === 'Ambos') {
                alert("Para encaminhamento de Consulta ou Ambos, 'ID do Novo Agendamento' e 'ID do Novo Paciente' são obrigatórios.");
                return;
            }
        }

        await apiFetch(`${API_BASE_URL}/encaminhamentos`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
        encaminhamentoForm.reset();
        document.getElementById('enc-exames-group').style.display = 'none';
        document.getElementById('enc-agendamento-group').style.display = 'none';
        alert('Encaminhamento criado com sucesso!');
    });

    document.getElementById('lookup-enc-btn').addEventListener('click', async () => {
        const id = document.getElementById('lookup-enc-id').value;
        const detailsDiv = document.getElementById('encaminhamento-details');
        detailsDiv.innerHTML = '';

        if (!id) {
            detailsDiv.innerHTML = '<p>Por favor, digite o ID do Encaminhamento.</p>';
            return;
        }
        try {
            const enc = await apiFetch(`${API_BASE_URL}/encaminhamentos/${id}`);

            let detailsHtml = `<h4>Detalhes do Encaminhamento #${enc.id_encaminhamento}</h4>
                               <p><strong>Agendamento de Origem:</strong> ID ${enc.id_agendamento} (Paciente: ${enc.id_paciente})</p>
                               <p><strong>Tipo:</strong> ${enc.tipo}</p>
                               <p><strong>Observações:</strong> ${enc.observacoes || 'Nenhuma'}</p>`;

            if (enc.tipo === 'Exame' || enc.tipo === 'Ambos') {
                if (enc.exames && enc.exames.length > 0) {
                    detailsHtml += '<h5>Exames Solicitados:</h5><ul>';
                    enc.exames.forEach(ex => detailsHtml += `<li>${ex.nome} (ID: ${ex.id_exame})</li>`);
                    detailsHtml += '</ul>';
                } else {
                    detailsHtml += '<p>Nenhum exame detalhado para este encaminhamento.</p>';
                }
            }
            if (enc.tipo === 'Consulta' || enc.tipo === 'Ambos') {
                if (enc.consulta_agendada) {
                    detailsHtml += `<h5>Nova Consulta Agendada:</h5>
                                    <p><strong>ID Agendamento:</strong> ${enc.consulta_agendada.id_agendamento}</p>
                                    <p><strong>ID Paciente (Nova Consulta):</strong> ${enc.consulta_agendada.id_paciente}</p>
                                    <p><strong>Data:</strong> ${new Date(enc.consulta_agendada.data).toLocaleString('pt-BR')}</p>`;
                } else {
                    detailsHtml += '<p>Nenhuma nova consulta agendada detalhada para este encaminhamento.</p>';
                }
            }
            detailsDiv.innerHTML = detailsHtml;
        } catch (error) {
            detailsDiv.innerHTML = `<p>Erro ao buscar encaminhamento: ${error.message}</p>`;
        }
    });

    const medicosTbody = document.getElementById('medicos-tbody');
    const medicoForm = document.getElementById('medico-form');

    const renderMedicos = (medicos) => {
        medicosTbody.innerHTML = '';
        if (medicos.length === 0) {
            medicosTbody.innerHTML = '<tr><td colspan="4">Nenhum médico encontrado.</td></tr>';
            return;
        }
        medicos.forEach(med => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${med.crm}</td>
                <td>${med.nome}</td>
                <td>${med.especialidade}</td>
                <td class="action-buttons">
                    <button class="edit-btn" onclick="setupEditForm('medico', '${med.crm}')">Editar</button>
                    <button class="delete-btn" onclick="deleteItem('medico', '${med.crm}')">Deletar</button>
                </td>
            `;
            medicosTbody.appendChild(tr);
        });
    };

    const loadMedicos = () => apiFetch(`${API_BASE_URL}/medicos`).then(renderMedicos);

    medicoForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const crmOriginal = document.getElementById('medico_crm_original').value;
        const crm = document.getElementById('med_crm').value;
        const nome = document.getElementById('med_nome').value;
        const especialidade = document.getElementById('med_especialidade').value;

        const isEditing = crmOriginal !== '';
        const method = isEditing ? 'PATCH' : 'POST';
        const url = isEditing ? `${API_BASE_URL}/medicos/${crmOriginal}` : `${API_BASE_URL}/medicos`;

        const body = isEditing ? { nome } : { crm, nome, especialidade };

        await apiFetch(url, { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
        resetForm('medico');
        loadMedicos();
    });

    const pacientesTbody = document.getElementById('pacientes-tbody');
    const pacienteForm = document.getElementById('paciente-form');
    const telefonesContainer = document.getElementById('pac_telefones_container');
    const addTelefoneBtn = document.getElementById('add_telefone_btn');

    const renderPacientes = (pacientes) => {
        pacientesTbody.innerHTML = '';
        if (pacientes.length === 0) {
            pacientesTbody.innerHTML = '<tr><td colspan="8">Nenhum paciente encontrado.</td></tr>';
            return;
        }
        pacientes.forEach(pac => {
            const tr = document.createElement('tr');
            const phonesHtml = pac.telefones.length > 0
                ? pac.telefones.map(t => `${t.numero} (${t.tipo})`).join('<br>')
                : 'N/A';
            tr.innerHTML = `
                <td>${pac.id_paciente}</td>
                <td>${pac.nome}</td>
                <td>${pac.data_nascimento}</td>
                <td>${pac.sexo}</td>
                <td>${pac.email || 'N/A'}</td>
                <td>${pac.cpf}</td>
                <td>${phonesHtml}</td>
                <td class="action-buttons">
                    <button class="edit-btn" onclick="setupEditForm('paciente', ${pac.id_paciente})">Editar</button>
                    <button class="delete-btn" onclick="deleteItem('paciente', ${pac.id_paciente})">Deletar</button>
                </td>
            `;
            pacientesTbody.appendChild(tr);
        });
    };

    const loadPacientes = () => apiFetch(`${API_BASE_URL}/pacientes`).then(renderPacientes);

    const addTelefoneInput = (numero = '', tipo = '') => {
        const div = document.createElement('div');
        div.classList.add('telefone-input-group');
        div.innerHTML = `
            <input type="text" class="telefone-numero" value="${numero}" placeholder="Número (Ex: 11987654321)" required>
            <select class="telefone-tipo" required>
                <option value="">Tipo</option>
                <option value="Celular" ${tipo === 'Celular' ? 'selected' : ''}>Celular</option>
                <option value="Residencial" ${tipo === 'Residencial' ? 'selected' : ''}>Residencial</option>
            </select>
            <button type="button" class="remove-telefone-btn delete-btn">Remover</button>
        `;
        telefonesContainer.appendChild(div);
        div.querySelector('.remove-telefone-btn').addEventListener('click', () => div.remove());
    };

    addTelefoneBtn.addEventListener('click', () => addTelefoneInput());

    pacienteForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const pacienteId = document.getElementById('paciente_id_original').value;
        const method = pacienteId ? 'PATCH' : 'POST';
        const url = pacienteId ? `${API_BASE_URL}/pacientes/${pacienteId}` : `${API_BASE_URL}/pacientes`;

        const telefones = Array.from(telefonesContainer.children).map(div => ({
            numero: div.querySelector('.telefone-numero').value,
            tipo: div.querySelector('.telefone-tipo').value
        }));

        const body = {
            nome: document.getElementById('pac_nome').value,
            sexo: document.getElementById('pac_sexo').value,
            email: document.getElementById('pac_email').value || null,
            telefones: telefones.length > 0 ? telefones : null
        };

        if (!pacienteId) {
            body.data_nascimento = document.getElementById('pac_data_nascimento').value;
            body.cpf = document.getElementById('pac_cpf').value;
        }

        await apiFetch(url, { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
        resetForm('paciente');
        loadPacientes();
    });

    const remarcasTbody = document.getElementById('remarcas-tbody');
    const remarcaForm = document.getElementById('remarca-form');

    const renderRemarcas = (remarcas) => {
        remarcasTbody.innerHTML = '';
        if (remarcas.length === 0) {
            remarcasTbody.innerHTML = '<tr><td colspan="6">Nenhuma remarca encontrada.</td></tr>';
            return;
        }
        remarcas.forEach(rem => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${rem.id_remarca}</td>
                <td>${rem.antigo_id_agendamento} / ${rem.antigo_id_paciente}</td>
                <td>${rem.novo_id_agendamento} / ${rem.novo_id_paciente}</td>
                <td>${rem.motivo || 'N/A'}</td>
                <td>${new Date(rem.data_remarcacao).toLocaleDateString('pt-BR')}</td>
                <td>${rem.quem_solicitou || 'N/A'}</td>
            `;
            remarcasTbody.appendChild(tr);
        });
    };

    const loadRemarcas = () => apiFetch(`${API_BASE_URL}/remarcas`).then(renderRemarcas);

    remarcaForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const body = {
            antigo_id_agendamento: parseInt(document.getElementById('rem_antigo_ag_id').value),
            antigo_id_paciente: parseInt(document.getElementById('rem_antigo_pac_id').value),
            novo_id_agendamento: parseInt(document.getElementById('rem_novo_ag_id').value),
            novo_id_paciente: parseInt(document.getElementById('rem_novo_pac_id').value),
            motivo: document.getElementById('rem_motivo').value || null,
            data_remarcacao: document.getElementById('rem_data_remarcacao').value,
            quem_solicitou: document.getElementById('rem_quem_solicitou').value || null
        };

        await apiFetch(`${API_BASE_URL}/remarcas`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
        resetForm('remarca');
        loadRemarcas();
    });


    const reportAgendamentosStatus = document.getElementById('report-agendamentos-status');
    const reportMedicosConsultas = document.getElementById('report-medicos-consultas');
    const reportEncaminhamentosTipo = document.getElementById('report-encaminhamentos-tipo');
    const reportPacientesCardiologia = document.getElementById('report-pacientes-cardiologia');
    const reportCategoriaPaciente = document.getElementById('report-categoria-paciente');
    const reportUltimoAgendamento = document.getElementById('report-ultimo-agendamento');
    const reportConsultasEncaminhamentos = document.getElementById('report-consultas-encaminhamentos');
    const reportExamesConsultasPaciente = document.getElementById('report-exames-consultas-paciente');


    const loadReports = async () => {
        try {
            const statusData = await apiFetch(`${API_BASE_URL}/relatorios/agendamentos-por-status`);
            reportAgendamentosStatus.innerHTML = '<ul>' + statusData.map(item => `<li><strong>${item.status}:</strong> ${item.total}</li>`).join('') + '</ul>';

            const medicosData = await apiFetch(`${API_BASE_URL}/relatorios/medicos-total-consultas`);
            reportMedicosConsultas.innerHTML = '<ul>' + medicosData.map(item => `<li><strong>${item.medico}:</strong> ${item.total_consultas} consultas</li>`).join('') + '</ul>';

            const encaminhamentosData = await apiFetch(`${API_BASE_URL}/relatorios/encaminhamentos-por-tipo`);
            reportEncaminhamentosTipo.innerHTML = '<ul>' + encaminhamentosData.map(item => `<li><strong>${item.tipo}:</strong> ${item.quantidade}</li>`).join('') + '</ul>';

            const pacientesCardioData = await apiFetch(`${API_BASE_URL}/relatorios/pacientes-cardiologia`);
            if (pacientesCardioData.length > 0) {
                reportPacientesCardiologia.innerHTML = '<ul>' + pacientesCardioData.map(item => `<li><strong>${item.paciente}:</strong> ${item.medico} (${item.especialidade})</li>`).join('') + '</ul>';
            } else {
                reportPacientesCardiologia.innerHTML = '<p>Nenhum paciente encontrado na cardiologia.</p>';
            }

            const categoriaPacienteData = await apiFetch(`${API_BASE_URL}/relatorios/categoria-paciente`);
            if (categoriaPacienteData.length > 0) {
                reportCategoriaPaciente.innerHTML = '<ul>' + categoriaPacienteData.map(item => `<li><strong>${item.nome}:</strong> ${item.categoria} (${item.total_agendamentos} agendamentos)</li>`).join('') + '</ul>';
            } else {
                reportCategoriaPaciente.innerHTML = '<p>Nenhuma categorização de paciente disponível.</p>';
            }

            const ultimoAgendamentoData = await apiFetch(`${API_BASE_URL}/relatorios/ultimo-agendamento-paciente`);
            if (ultimoAgendamentoData.length > 0) {
                reportUltimoAgendamento.innerHTML = '<ul>' + ultimoAgendamentoData.map(item => `<li><strong>${item.nome}:</strong> ${item.status} (Tel: ${item.telefone_paciente})</li>`).join('') + '</ul>';
            } else {
                reportUltimoAgendamento.innerHTML = '<p>Nenhum último agendamento disponível.</p>';
            }

            const consultasEncaminhamentosData = await apiFetch(`${API_BASE_URL}/relatorios/consultas-encaminhamentos`);
            if (consultasEncaminhamentosData.length > 0) {
                reportConsultasEncaminhamentos.innerHTML = '<ul>' + consultasEncaminhamentosData.map(item => `<li><strong>Paciente:</strong> ${item.nome_paciente} | <strong>Médico:</strong> ${item.nome_medico} (${item.especialidade}) | <strong>Diagnóstico:</strong> ${item.diagnostico} | <strong>Encaminhamento:</strong> ${item.tipo_encaminhamento}</li>`).join('') + '</ul>';
            } else {
                reportConsultasEncaminhamentos.innerHTML = '<p>Nenhum dado de consultas e encaminhamentos disponível.</p>';
            }

            const examesConsultasPacienteData = await apiFetch(`${API_BASE_URL}/relatorios/exames-consultas-por-paciente`);
            if (examesConsultasPacienteData.length > 0) {
                reportExamesConsultasPaciente.innerHTML = '<ul>' + examesConsultasPacienteData.map(item => `<li><strong>Paciente:</strong> ${item.nome_paciente} | <strong>Total Exames:</strong> ${item.count} | <strong>Exames Realizados:</strong> ${item.exames_realizados} | <strong>Total Consultas:</strong> ${item.total_consultas}</li>`).join('') + '</ul>';
            } else {
                reportExamesConsultasPaciente.innerHTML = '<p>Nenhum dado de exames e consultas por paciente disponível.</p>';
            }


        } catch (error) {
            console.error("Erro ao carregar relatórios:", error);
            reportAgendamentosStatus.innerHTML = `<p>Erro ao carregar relatório: ${error.message}</p>`;
            reportMedicosConsultas.innerHTML = `<p>Erro ao carregar relatório: ${error.message}</p>`;
            reportEncaminhamentosTipo.innerHTML = `<p>Erro ao carregar relatório: ${error.message}</p>`;
            reportPacientesCardiologia.innerHTML = `<p>Erro ao carregar relatório: ${error.message}</p>`;
            reportCategoriaPaciente.innerHTML = `<p>Erro ao carregar relatório: ${error.message}</p>`;
            reportUltimoAgendamento.innerHTML = `<p>Erro ao carregar relatório: ${error.message}</p>`;
            reportConsultasEncaminhamentos.innerHTML = `<p>Erro ao carregar relatório: ${error.message}</p>`;
            reportExamesConsultasPaciente.innerHTML = `<p>Erro ao carregar relatório: ${error.message}</p>`;
        }
    };

    window.setupEditForm = async (type, ...ids) => {
        if (type === 'agendamento') {
            const [id_agendamento, id_paciente] = ids;
            const ag = await apiFetch(`${API_BASE_URL}/agendamentos/${id_agendamento}/${id_paciente}`);
            document.getElementById('agendamento-form-title').textContent = 'Editar Agendamento';
            document.getElementById('agendamento_id').value = ag.id_agendamento;
            document.getElementById('ag_id_paciente').value = ag.id_paciente;
            document.getElementById('ag_data_hora').value = new Date(ag.data).toISOString().slice(0, 16);
            document.getElementById('ag_observacoes').value = ag.observacoes || '';
            document.getElementById('ag_status').value = ag.status;
            document.getElementById('ag_status_group').style.display = 'block';
            document.getElementById('cancel-ag-edit-btn').style.display = 'block';
            document.getElementById('ag_id_paciente').disabled = true;
            document.getElementById('ag_data_hora').disabled = true;

        } else if (type === 'consulta') {
            const [crm, id_agendamento, id_paciente] = ids[0].split('|');
            const con = await apiFetch(`${API_BASE_URL}/consultas/${crm}/${id_agendamento}/${id_paciente}`);
            document.getElementById('consulta-form-title').textContent = 'Editar Consulta';
            document.getElementById('consulta_id').value = 'editing';
            document.getElementById('con_crm').value = con.crm;
            document.getElementById('con_id_agendamento').value = con.id_agendamento;
            document.getElementById('con_id_paciente').value = con.id_paciente;
            document.getElementById('con_data_hora').value = new Date(con.data_hora).toISOString().slice(0, 16);
            document.getElementById('con_diagnostico').value = con.diagnostico || '';
            document.getElementById('con_observacoes').value = con.observacoes || '';
            document.getElementById('cancel-con-edit-btn').style.display = 'block';
            ['con_crm', 'con_id_agendamento', 'con_id_paciente', 'con_data_hora'].forEach(elId =>
                document.getElementById(elId).disabled = true
            );
        } else if (type === 'medico') {
            const crm = ids[0];
            const med = await apiFetch(`${API_BASE_URL}/medicos/${crm}`);
            document.getElementById('medico-form-title').textContent = 'Editar Médico';
            document.getElementById('medico_crm_original').value = med.crm;
            document.getElementById('med_crm').value = med.crm;
            document.getElementById('med_nome').value = med.nome;
            document.getElementById('med_especialidade').value = med.especialidade;
            document.getElementById('cancel-med-edit-btn').style.display = 'block';
            document.getElementById('med_crm').disabled = true;
            document.getElementById('med_especialidade').disabled = true;
        } else if (type === 'paciente') {
            const id_paciente = ids[0];
            const pac = await apiFetch(`${API_BASE_URL}/pacientes/${id_paciente}`);
            document.getElementById('paciente-form-title').textContent = 'Editar Paciente';
            document.getElementById('paciente_id_original').value = pac.id_paciente;
            document.getElementById('pac_nome').value = pac.nome;
            document.getElementById('pac_data_nascimento').value = pac.data_nascimento;
            document.getElementById('pac_sexo').value = pac.sexo;
            document.getElementById('pac_email').value = pac.email || '';
            document.getElementById('pac_cpf').value = pac.cpf;
            document.getElementById('cancel-pac-edit-btn').style.display = 'block';
            document.getElementById('pac_data_nascimento').disabled = true;
            document.getElementById('pac_cpf').disabled = true;

            telefonesContainer.innerHTML = '';
            if (pac.telefones && pac.telefones.length > 0) {
                pac.telefones.forEach(tel => addTelefoneInput(tel.numero, tel.tipo));
            } else {
                addTelefoneInput();
            }
        }
    };

    window.deleteItem = async (type, id) => {
        if (type === 'agendamento' && confirm('Tem certeza que deseja cancelar este agendamento?')) {
            const [id_agendamento, id_paciente] = id.split('|').map(Number);
            await apiFetch(`${API_BASE_URL}/agendamentos/${id_agendamento}/${id_paciente}`, { method: 'DELETE' });
            loadAgendamentos();
        } else if (type === 'consulta' && confirm('Confirma a exclusão da consulta?')) {
            const [crm, id_agendamento, id_paciente] = id.split('|');
            await apiFetch(`${API_BASE_URL}/consultas/${crm}/${id_agendamento}/${id_paciente}`, {
                method: 'DELETE'
            });
            loadConsultas();
        } else if (type === 'medico' && confirm('Tem certeza que deseja deletar este médico?')) {
            await apiFetch(`${API_BASE_URL}/medicos/${id}`, { method: 'DELETE' });
            loadMedicos();
        } else if (type === 'paciente' && confirm('Tem certeza que deseja deletar este paciente? Isso removerá também seus telefones e poderá afetar agendamentos, consultas e encaminhamentos associados.')) {
            await apiFetch(`${API_BASE_URL}/pacientes/${id}`, { method: 'DELETE' });
            loadPacientes();
        }
    };

    const resetForm = (type) => {
        if (type === 'agendamento') {
            agendamentoForm.reset();
            document.getElementById('agendamento-form-title').textContent = 'Novo Agendamento';
            document.getElementById('agendamento_id').value = '';
            document.getElementById('ag_status_group').style.display = 'none';
            document.getElementById('cancel-ag-edit-btn').style.display = 'none';
            document.getElementById('ag_id_paciente').disabled = false;
            document.getElementById('ag_data_hora').disabled = false;
        } else if (type === 'consulta') {
            consultaForm.reset();
            document.getElementById('consulta-form-title').textContent = 'Nova Consulta';
            document.getElementById('consulta_id').value = '';
            document.getElementById('cancel-con-edit-btn').style.display = 'none';
            ['con_crm', 'con_id_agendamento', 'con_id_paciente', 'con_data_hora'].forEach(elId => document.getElementById(elId).disabled = false);
        } else if (type === 'medico') {
            medicoForm.reset();
            document.getElementById('medico-form-title').textContent = 'Novo Médico';
            document.getElementById('medico_crm_original').value = '';
            document.getElementById('cancel-med-edit-btn').style.display = 'none';
            document.getElementById('med_crm').disabled = false;
            document.getElementById('med_especialidade').disabled = false;
        } else if (type === 'paciente') {
            pacienteForm.reset();
            document.getElementById('paciente-form-title').textContent = 'Novo Paciente';
            document.getElementById('paciente_id_original').value = '';
            document.getElementById('cancel-pac-edit-btn').style.display = 'none';
            document.getElementById('pac_data_nascimento').disabled = false;
            document.getElementById('pac_cpf').disabled = false;
            telefonesContainer.innerHTML = '';
            addTelefoneInput();
        } else if (type === 'remarca') {
            remarcaForm.reset();
        }
    };

    document.getElementById('cancel-ag-edit-btn').addEventListener('click', () => resetForm('agendamento'));
    document.getElementById('cancel-con-edit-btn').addEventListener('click', () => resetForm('consulta'));
    document.getElementById('cancel-med-edit-btn').addEventListener('click', () => resetForm('medico'));
    document.getElementById('cancel-pac-edit-btn').addEventListener('click', () => resetForm('paciente'));

});