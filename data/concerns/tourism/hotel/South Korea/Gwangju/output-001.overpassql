[out:json][timeout:30];
area["name:en"="Gwangju"]->.searchArea;
(
  nwr["tourism"="hotel"](area.searchArea);
);
out geom;