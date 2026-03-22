[out:json][timeout:30];
area["name:en"="Helsinki"]->.searchArea;
(
  nwr["tourism"="museum"](area.searchArea);
);
out geom;