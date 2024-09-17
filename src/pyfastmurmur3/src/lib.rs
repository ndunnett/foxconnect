use pyo3::prelude::*;

#[pyfunction]
fn hash(text: &str) -> isize {
    fastmurmur3::hash(text.as_bytes()) as isize
}

#[pymodule]
#[pyo3(name = "fastmurmur3")]
fn pyfastmurmur3(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(hash, m)?)
}
