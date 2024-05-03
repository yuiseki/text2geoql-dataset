[out:json][timeout:30000];
area["name:en"="Kosovo"]->.searchArea;
(
  relation["boundary"="administrative"]["name:en"="Pristina"](area.searchArea);
);
out geom;
