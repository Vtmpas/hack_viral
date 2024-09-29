Here’s how you can structure the README with two images displayed in a horizontal table and instructions on how to run the application:

---

## Upload Page Preview

<table>
  <tr>
    <td><img src="public/images/start_page.jpg" alt="start_page.jpg_preview" width="400"/></td>
    <td><img src="public/images/upload_page.jpg" alt="upload_page_preview" width="400"/></td>
  </tr>
</table>

## Instructions to Run

### Docker Setup
To start the server, you can use Docker Compose with the following command:

```bash
docker compose up -d --build
```

### Running the Frontend Service (for development)
1. Install dependencies:
   ```bash
   npm install
   ```
2. Run the development server:
   ```bash
   npm run dev
   ```
