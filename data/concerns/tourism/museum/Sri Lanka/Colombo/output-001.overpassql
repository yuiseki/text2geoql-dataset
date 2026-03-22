[out:json][timeout:30];
area["name:en"="Colombo"]->.searchArea;
(
  nwr["tourism"="museum"](area.searchArea);
);
out geom;