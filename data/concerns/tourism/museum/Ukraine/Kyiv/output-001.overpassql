[out:json][timeout:30];
area["name:en"="Kyiv"]->.searchArea;
(
  nwr["tourism"="museum"](area.searchArea);
);
out geom;