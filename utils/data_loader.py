import pandas as pd
import streamlit as st
import os

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

@st.cache_data
def load_assets():
    df = pd.read_csv(f"{DATA}/critical_assets.csv")
    df["expected_delivery"] = pd.to_datetime(df["expected_delivery"])
    df["actual_delivery"] = pd.to_datetime(df["actual_delivery"], errors="coerce")
    df["order_date"] = pd.to_datetime(df["order_date"])
    return df

@st.cache_data
def load_deps(): return pd.read_csv(f"{DATA}/dependencies.csv")

@st.cache_data
def load_checklist(): return pd.read_csv(f"{DATA}/commissioning_checklist.csv")

@st.cache_data
def load_specs(): return pd.read_csv(f"{DATA}/specifications_knowledge.csv")

@st.cache_data
def load_milestones():
    df = pd.read_csv(f"{DATA}/milestones.csv")
    df["planned_date"] = pd.to_datetime(df["planned_date"])
    df["forecast_date"] = pd.to_datetime(df["forecast_date"])
    return df
