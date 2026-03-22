[out:json][timeout:30];
area["name:en"="Gwangju"]->.searchArea;
(
  nwr["tourism"="museum"](area.searchArea);
);
out geom;