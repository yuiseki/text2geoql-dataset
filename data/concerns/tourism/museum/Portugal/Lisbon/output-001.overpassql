[out:json][timeout:30];
area["name:en"="Lisbon"]->.searchArea;
(
  nwr["tourism"="museum"](area.searchArea);
);
out geom;