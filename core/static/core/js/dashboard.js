document.addEventListener('DOMContentLoaded', function () {
    const dataInicioInput = document.getElementById('data_inicio');
    const dataFimInput = document.getElementById('data_fim');
    const moedasCheckboxes = document.querySelectorAll('input[name="moeda"]');
    const statusMsgDiv = document.getElementById('status-msg');

    function renderizarGraficoAbsoluto(dados) {
        const series = {};
        const limiarMagnitude = 50; // limite para decidir qual eixo Y usar

        dados.forEach(cotacao => {
            const moeda = cotacao.moeda;
            const valor = parseFloat(cotacao.valor);
            if (!series[moeda]) {
                series[moeda] = { name: moeda, data: [], yAxis: valor < limiarMagnitude ? 0 : 1 };
            }
            series[moeda].data.push([new Date(cotacao.data).getTime(), valor]);
        });

        Highcharts.chart('chart-absolute', {
            title: { text: 'Cotações em Valores Absolutos (USD/Moeda)' },
            chart: { type: 'line', zoomType: 'x' },
            xAxis: { type: 'datetime' },
            yAxis: [{ title: { text: 'Cotação (BRL, EUR)' } }, { title: { text: 'Cotação (JPY)' }, opposite: true }],
            tooltip: { shared: true },
            plotOptions: { series: { marker: { enabled: true, radius: 3 } } },
            series: Object.values(series)
        });
    }

    function renderizarGraficoPercentual(dados) {
        const series = {};
        const baseValues = {};

        dados.forEach(cotacao => {
            if (!baseValues[cotacao.moeda]) baseValues[cotacao.moeda] = parseFloat(cotacao.valor);
        });

        dados.forEach(cotacao => {
            const moeda = cotacao.moeda;
            if (!series[moeda]) series[moeda] = { name: moeda, data: [] };
            const valor = parseFloat(cotacao.valor);
            const percentageChange = ((valor / baseValues[moeda]) - 1) * 100;
            series[moeda].data.push({ x: new Date(cotacao.data).getTime(), y: percentageChange, originalValue: valor });
        });

        Highcharts.chart('chart-percentage', {
            title: { text: 'Variação Percentual da Cotação (USD/Moeda)' },
            chart: { type: 'line' },
            xAxis: { type: 'datetime' },
            yAxis: { title: { text: 'Variação (%)' }, labels: { format: '{value:.2f}%' } },
            tooltip: { pointFormat: '<span style="color:{point.color}">●</span> {series.name}: <b>{point.y:.2f}%</b> (Cotação: <b>{point.originalValue:.4f}</b>)<br/>', shared: true },
            series: Object.values(series)
        });
    }

    function renderizarGraficoPerformance(dados) {
        const dadosPorMoeda = {};

        dados.forEach(cotacao => {
            if (!dadosPorMoeda[cotacao.moeda]) {
                dadosPorMoeda[cotacao.moeda] = [];
            }
            dadosPorMoeda[cotacao.moeda].push(parseFloat(cotacao.valor));
        });

        const seriesData = Object.keys(dadosPorMoeda).map(moeda => {
            const valores = dadosPorMoeda[moeda];
            const startValue = 1 / valores[0];
            const endValue = 1 / valores[valores.length - 1];
            const performance = ((endValue / startValue) - 1) * 100;
            
            return { 
                name: moeda, 
                y: performance, 
                // verde se valorizou (positivo), vermelho se desvalorizou (negativo)
                color: performance >= 0 ? '#28a745' : '#dc3545' 
            };
        });

        Highcharts.chart('chart-performance', {
            title: { text: 'Valorização da Moeda vs. Dólar' },
            chart: { type: 'bar' },
            xAxis: { categories: Object.keys(dadosPorMoeda), title: { text: null } },
            yAxis: { title: { text: 'Valorização (%)' }, labels: { format: '{value:.2f}%' } },
            plotOptions: { bar: { dataLabels: { enabled: true, format: '{y:.2f}%' } } },
            legend: { enabled: false },
            series: [{ name: 'Valorização', data: seriesData }]
        });
    }

    function atualizarGraficos() {
        const dataInicio = dataInicioInput.value;
        const dataFim = dataFimInput.value;
        const moedasSelecionadas = Array.from(document.querySelectorAll('input[name="moeda"]:checked')).map(cb => cb.value);

        if (!dataInicio || !dataFim || moedasSelecionadas.length === 0) {
            return;
        }

        const moedasStr = moedasSelecionadas.join(',');
        const apiUrl = `/api/grafico/?data_inicio=${dataInicio}&data_fim=${dataFim}&moedas=${moedasStr}`;

        statusMsgDiv.textContent = 'Buscando dados...';
        statusMsgDiv.className = 'status-loading';
        statusMsgDiv.style.display = 'block';

        fetch(apiUrl)
            .then(response => {
                if (!response.ok) return response.json().then(err => { throw new Error(err.error) });
                return response.json();
            })
            .then(dados => {
                if (dados.length === 0) {
                    throw new Error('Nenhuma cotação encontrada para o período e moedas selecionados.');
                }
                statusMsgDiv.style.display = 'none';
                
                dados.sort((a, b) => new Date(a.data) - new Date(b.data));
                
                renderizarGraficoAbsoluto(dados);
                renderizarGraficoPercentual(dados);
                renderizarGraficoPerformance(dados);
            })
            .catch(error => {
                console.error('Erro ao buscar dados:', error);
                statusMsgDiv.textContent = `Erro: ${error.message}`;
                statusMsgDiv.className = 'status-error';
                document.getElementById('chart-absolute').innerHTML = '';
                document.getElementById('chart-percentage').innerHTML = '';
                document.getElementById('chart-performance').innerHTML = '';
            });
    }

    function setDefaultDates() {
        const hoje = MAX_DATA_DISPONIVEL ? new Date(MAX_DATA_DISPONIVEL + 'T00:00:00') : new Date();
        const cincoDiasAtras = new Date();
        cincoDiasAtras.setDate(hoje.getDate() - 5);
        
        dataFimInput.value = hoje.toISOString().split('T')[0];
        dataInicioInput.value = cincoDiasAtras.toISOString().split('T')[0];
    }

    setDefaultDates();
    atualizarGraficos();

    dataInicioInput.addEventListener('change', atualizarGraficos);
    dataFimInput.addEventListener('change', atualizarGraficos);
    moedasCheckboxes.forEach(cb => cb.addEventListener('change', atualizarGraficos));
});