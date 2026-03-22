[out:json][timeout:30];
area["name:en"="Vienna"]->.searchArea;
(
  nwr["tourism"="museum"](area.searchArea);
);
out geom;