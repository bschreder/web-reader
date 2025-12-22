import type { FC } from 'react';

interface Props {
  answer: string
  citations: Array<{ title: string; url: string }>
  confidence: number
}

const AnswerDisplay: FC<Props> = ({ answer, citations, confidence }) => {
  return (
    <div className="space-y-3">
      <div className="prose prose-invert max-w-none">
        {answer.split('\n').map((p, i) => (
          <p key={i}>{p}</p>
        ))}
      </div>
      <div>
        <h3 className="text-lg font-semibold">Citations</h3>
        <ul className="list-disc pl-6">
          {citations.map((c) => (
            <li key={c.url}>
              <a href={c.url} target="_blank" rel="noreferrer" className="text-blue-400 hover:underline">
                {c.title}
              </a>
            </li>
          ))}
        </ul>
      </div>
      <div>
        <span className="text-sm text-neutral-400">Confidence:</span>{' '}
        <span className="font-semibold">{Math.round(confidence * 100)}%</span>
      </div>
    </div>
  );
};

export default AnswerDisplay;
