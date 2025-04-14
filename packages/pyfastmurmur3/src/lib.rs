use pyo3::prelude::*;

#[pyfunction]
fn murmur3(content: &[u8]) -> isize {
    fastmurmur3::hash(content) as isize
}

#[pymodule]
#[pyo3(name = "fastmurmur3")]
fn pyfastmurmur3(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(murmur3, m)?)
}
