import streamlit as st
import streamlit.components.v1 as components

@st.cache_data
def star_rating_component():
    components.html(
        """
        <style>
        .star-rating {
            direction: rtl;
            font-size: 2rem;
            unicode-bidi: bidi-override;
            display: inline-flex;
        }
        .star-rating input {
            display: none;
        }
        .star-rating label {
            color: #ccc;
            cursor: pointer;
        }
        .star-rating input:checked ~ label,
        .star-rating label:hover,
        .star-rating label:hover ~ label {
            color: gold;
        }
        </style>

        <form>
            <div class="star-rating">
                <input type="radio" name="rating" id="5" value="5"><label for="5">★</label>
                <input type="radio" name="rating" id="4" value="4"><label for="4">★</label>
                <input type="radio" name="rating" id="3" value="3"><label for="3">★</label>
                <input type="radio" name="rating" id="2" value="2"><label for="2">★</label>
                <input type="radio" name="rating" id="1" value="1"><label for="1">★</label>
            </div>
        </form>
        """,
        height=120,
    )
