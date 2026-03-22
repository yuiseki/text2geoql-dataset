[out:json][timeout:30];
area["name:en"="Zurich"]->.searchArea;
(
  nwr["tourism"="museum"](area.searchArea);
);
out geom;