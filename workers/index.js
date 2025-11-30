// GitHub Badge API - Cloudflare Workers Version
// Simple badge generation for Workers

const GITHUB_API_BASE = 'https://api.github.com/repos/';

const THEMES = {
  flat: {
    template: `<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="20">
<rect width="100%" height="100%" fill="{bg_color}"/>
<text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="{text_color}" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">{label}: {value}</text>
</svg>`,
    bg_color: '#555',
    text_color: '#fff'
  }
};

function generateBadge(label, value, style = 'flat', color = null) {
  const theme = THEMES[style] || THEMES.flat;
  const bgColor = color || '#4c1';
  const textColor = theme.text_color;
  const width = Math.max(80, (label.length + value.length) * 8 + 20);

  return theme.template
    .replace('{width}', width)
    .replace('{bg_color}', bgColor)
    .replace('{text_color}', textColor)
    .replace('{label}', label)
    .replace('{value}', value);
}

async function fetchGitHubMetric(owner, repo, metric, token) {
  const headers = { 'Accept': 'application/vnd.github.v3+json' };
  if (token) headers['Authorization'] = `token ${token}`;

  const response = await fetch(`${GITHUB_API_BASE}${owner}/${repo}`, { headers });
  if (!response.ok) throw new Error('GitHub API error');

  const data = await response.json();

  switch (metric) {
    case 'stars': return data.stargazers_count?.toString() || '0';
    case 'forks': return data.forks_count?.toString() || '0';
    case 'issues': return data.open_issues_count?.toString() || '0';
    default: return 'unknown';
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;

    // CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET',
      'Access-Control-Allow-Headers': 'Content-Type',
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    try {
      // /badge/github/{owner}/{repo}/{metric}
      const githubMatch = path.match(/^\/badge\/github\/([^\/]+)\/([^\/]+)\/(.+)$/);
      if (githubMatch) {
        const [, owner, repo, metric] = githubMatch;
        const style = url.searchParams.get('style') || 'flat';
        const color = url.searchParams.get('color');

        const value = await fetchGitHubMetric(owner, repo, metric, env.GITHUB_TOKEN);
        const svg = generateBadge(metric, value, style, color);

        return new Response(svg, {
          headers: {
            ...corsHeaders,
            'Content-Type': 'image/svg+xml',
            'Cache-Control': 'public, max-age=300',
          },
        });
      }

      // /badge/custom
      if (path === '/badge/custom') {
        const label = url.searchParams.get('label') || 'Badge';
        const value = url.searchParams.get('value') || 'Value';
        const style = url.searchParams.get('style') || 'flat';
        const color = url.searchParams.get('color');

        const svg = generateBadge(label, value, style, color);

        return new Response(svg, {
          headers: {
            ...corsHeaders,
            'Content-Type': 'image/svg+xml',
            'Cache-Control': 'public, max-age=300',
          },
        });
      }

      // Health check
      if (path === '/health') {
        return new Response(JSON.stringify({ status: 'healthy', version: '2.0.0' }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        });
      }

      return new Response('Not Found', { status: 404, headers: corsHeaders });

    } catch (error) {
      console.error(error);
      const errorSvg = generateBadge('error', 'unknown', 'flat', 'red');
      return new Response(errorSvg, {
        status: 500,
        headers: {
          ...corsHeaders,
          'Content-Type': 'image/svg+xml',
        },
      });
    }
  },
};