const fs = require('fs');
const { promises: fs_promises } = require('fs');
const path = require('path');
const csv = require('csv-parser');
const jsonServer = require('json-server');

const PORT = 3001;
const DATA_DIR = path.join(__dirname, 'data');

/**
 * Asynchronously reads all CSV files from the /data directory
 * and converts them to a JSON object.
 * @returns {Promise<object>} A promise that resolves to the database object.
 */
async function createDbAsync() {
    const db = {};

    try {
        // 1. Find all CSV files in the 'data' directory
        const files = await fs_promises.readdir(DATA_DIR);
        const csvFiles = files.filter(file => path.extname(file) === '.csv');

        if (csvFiles.length === 0) {
            console.warn(`No CSV files found in ${DATA_DIR}.`);
            console.warn("The API will start with no data. Please add CSVs to the /data folder."); // <-- Fixed this line
            return db;
        }

        console.log('Found CSV files. Starting data load...');

        // 2. Create an array of promises, one for each file to be read
        const readPromises = csvFiles.map(file => {
            return new Promise((resolve, reject) => {
                const name = path.basename(file, '.csv');
                const data = [];
                const filePath = path.join(DATA_DIR, file);

                // 3. Use a stream to read each file
                fs.createReadStream(filePath)
                    .pipe(csv())
                    .on('data', (row) => {
                        data.push(row);
                    })
                    .on('end', () => {
                        db[name] = data; // Add the data to our db object
                        console.log(`  [+] Successfully loaded data for '${name}' from ${file}`);
                        resolve();
                    })
                    .on('error', (err) => {
                        console.error(`Error reading file ${file}:`, err);
                        reject(err);
                    });
            });
        });

        // 4. Wait for ALL files to finish reading
        await Promise.all(readPromises);
        console.log('All data loaded successfully.');
        return db;

    } catch (err) {
        if (err.code === 'ENOENT') {
            console.error(`Error: Data directory not found at ${DATA_DIR}`);
            console.error("Please create a 'data' folder and add your CSV files."); // <-- Fixed this line
        } else {
            console.error('Error reading data directory:', err);
        }
        process.exit(1); // Exit if we can't read the data
    }
}

/**
 * Main function to create the DB and start the server
 */
async function startServer() {
    console.log("--- startServer() function called ---"); // New log
    // 5. Wait for the database to be created
    const db = await createDbAsync();

    if (!db) {
        console.error('Failed to create database. Exiting.');
        return;
    }

    // 6. Start the JSON server with our new data
    const server = jsonServer.create();
    const router = jsonServer.router(db);
    const middlewares = jsonServer.defaults();
    
    server.use(middlewares);
    server.use(router);

    // 7. Listen on the port and give confirmation
    server.listen(PORT, () => {
        console.log('\n=======================================');
        console.log(`  JSON Server is running!`);
        console.log('=======================================');
        console.log(`\nAvailable endpoints:`);
        
        Object.keys(db).forEach(name => {
            console.log(`  http://localhost:${PORT}/${name} (${db[name].length} items)`);
        });

        console.log('\nView the whole database at:');
        console.log(`  http://localhost:${PORT}/db`);
        console.log('\nPress CTRL+C to stop the server.');
    });
}

// Run the server
console.log("--- Starting server.js script... ---"); // New log

// Added a catch block to see any top-level errors
startServer().catch(err => {
    console.error("\nA critical unhandled error occurred:");
    console.error(err);
    process.exit(1);
});

