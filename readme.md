# Wedding Web with Gift Reservation System

Welcome to my Wedding Web repository! This project is built using Flask to create a website to share information with our guests with option to reserve wedding gifts for our special day.

## Main Feature description

**Gift Reservation**
- Users can browse through the list of available gifts and reserve the ones they wish to gift us for our wedding
- Gifts are loaded from `static/yaml/gifts.yml` file and their parameters are loaded from database
- Currently only available database option is MySQL
- In database are stored data about gift claim status, gift free code and last user reservation IP

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/Davisiiiik/wedding_web.git
    ```

2. Navigate to the project directory:

    ```bash
    cd wedding_web
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Copy and configure the default config file:

    ```bash
    cp static/yaml/config.default.yml static/yaml/config.yml
    nano static/yaml/config.yml
    ```

5. Run the application:

    ```bash
    python app.py
    ```

## Usage

1. Visit the website (by default: `http://localhost:2000`) on your web browser
2. Browse through the list of gifts and select the ones you'd like to reserve
3. On reservation a free code for that specific gift will be shared with you
4. In case you don't want that gift anymore, you can free it by providing free code from previous step

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
