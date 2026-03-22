[out:json][timeout:30];
area["name:en"="Incheon"]->.searchArea;
(
  nwr["tourism"="museum"](area.searchArea);
);
out geom;