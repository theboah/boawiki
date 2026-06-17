module.exports = {
    petstore: {
        output: {
            mode: 'tags-split',
            target: './src/generated/api.ts',
            schemas: './src/generated/model',
            client: 'react-query', // This is the magic that creates React hooks!
            mock: false,
        },
        input: {
            target: 'http://localhost:5000/openapi.json', // Path to your local schema or backend URL (e.g., http://localhost:8000/openapi.json)
        },
    },
};