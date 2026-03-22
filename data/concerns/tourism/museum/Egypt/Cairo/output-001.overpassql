[out:json][timeout:30];
area["name:en"="Cairo"]->.searchArea;
(
  nwr["tourism"="museum"](area.searchArea);
);
out geom;