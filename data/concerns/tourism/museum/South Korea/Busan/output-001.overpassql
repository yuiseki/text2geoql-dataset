[out:json][timeout:30];
area["name:en"="Busan"]->.searchArea;
(
  nwr["tourism"="museum"](area.searchArea);
);
out geom;