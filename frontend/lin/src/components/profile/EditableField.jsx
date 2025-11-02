import React, { useState, useEffect, useRef } from 'react';

// --- Icons ---
const EditIcon = () => ( <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L6.832 19.82a4.5 4.5 0 01-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 011.13-1.897L16.863 4.487zm0 0L19.5 7.125" /></svg> );
const SaveIcon = () => ( <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" /></svg> );

function EditableField({ initialValue, onSave, fieldName }) {
    const [isEditing, setIsEditing] = useState(false);
    const [value, setValue] = useState(initialValue);
    const wrapperRef = useRef(null); // Ref for the component's wrapper div

    // Function to handle saving the data
    const handleSave = () => {
        // Only call onSave if the value has actually changed
        if (value !== initialValue) {
            onSave(fieldName, value);
        }
        setIsEditing(false);
    };

    // Function to cancel editing
    const handleCancel = () => {
        setValue(initialValue); // Revert to original value
        setIsEditing(false);
    };

    // Focus the input when editing starts
    useEffect(() => {
        if (isEditing && wrapperRef.current) {
            const inputElement = wrapperRef.current.querySelector('input');
            if (inputElement) {
                inputElement.focus();
            }
        }
    }, [isEditing]);

    // Add event listener to detect clicks outside the component
    useEffect(() => {
        function handleClickOutside(event) {
            // If the ref exists and the click was outside of it, cancel editing.
            if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
                handleCancel();
            }
        }

        if (isEditing) {
            document.addEventListener("mousedown", handleClickOutside);
        }
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, [isEditing, initialValue]); // Rerun effect if isEditing or initialValue changes


    return (
        <div className="editable-field-container" ref={wrapperRef}>
            {isEditing ? (
                <>
                    <input
                        type="text"
                        value={value}
                        onChange={(e) => setValue(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSave()}
                        className="editable-field-input"
                    />
                    {/* FIX: Use onMouseDown to fire before the input's blur event */}
                    <button onMouseDown={handleSave} className="editable-field-icon-button save-icon">
                        <SaveIcon />
                    </button>
                </>
            ) : (
                <>
                    <span>{initialValue}</span>
                    <button onClick={() => setIsEditing(true)} className="editable-field-icon-button">
                        <EditIcon />
                    </button>
                </>
            )}
        </div>
    );
}

export default EditableField;
