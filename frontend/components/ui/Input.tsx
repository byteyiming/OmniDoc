'use client';

import { InputHTMLAttributes, TextareaHTMLAttributes, forwardRef } from 'react';
import { cn } from '@/lib/utils';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, helperText, id, ...props }, ref) => {
    const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;
    
    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={inputId}
            className="block text-sm font-semibold text-[#343A40] mb-2"
          >
            {label}
            {props.required && <span className="text-red-500 ml-1">*</span>}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          className={cn(
            'w-full rounded border-2 border-[#ADB5BD] bg-white px-2 py-2 text-base text-[#343A40]',
            'placeholder:text-[#ADB5BD]',
            'transition-all duration-200',
            'focus:border-[#007BFF] focus:outline-none focus:ring-4 focus:ring-[rgba(0,123,255,0.25)]',
            'hover:border-[#6C757D]',
            'disabled:cursor-not-allowed disabled:opacity-50 disabled:bg-[#F8F9FA]',
            error && 'border-red-500 focus:border-red-500 focus:ring-red-200',
            className
          )}
          {...props}
        />
        {error && (
          <p className="mt-1 text-sm text-red-600" role="alert">
            {error}
          </p>
        )}
        {helperText && !error && (
          <p className="mt-1 text-sm text-[#6C757D]">
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, label, error, helperText, id, ...props }, ref) => {
    const textareaId = id || `textarea-${Math.random().toString(36).substr(2, 9)}`;
    
    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={textareaId}
            className="block text-sm font-semibold text-[#343A40] mb-2"
          >
            {label}
            {props.required && <span className="text-red-500 ml-1">*</span>}
          </label>
        )}
        <textarea
          ref={ref}
          id={textareaId}
          className={cn(
            'w-full rounded border-2 border-[#ADB5BD] bg-white px-2 py-2 text-base text-[#343A40]',
            'placeholder:text-[#ADB5BD]',
            'transition-all duration-200',
            'focus:border-[#007BFF] focus:outline-none focus:ring-4 focus:ring-[rgba(0,123,255,0.25)]',
            'hover:border-[#6C757D]',
            'disabled:cursor-not-allowed disabled:opacity-50 disabled:bg-[#F8F9FA]',
            'resize-none',
            error && 'border-red-500 focus:border-red-500 focus:ring-red-200',
            className
          )}
          {...props}
        />
        {error && (
          <p className="mt-1 text-sm text-red-600" role="alert">
            {error}
          </p>
        )}
        {helperText && !error && (
          <p className="mt-1 text-sm text-[#6C757D]">
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Textarea.displayName = 'Textarea';

export default Input;

