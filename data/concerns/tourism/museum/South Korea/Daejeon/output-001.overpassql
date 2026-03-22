[out:json][timeout:30];
area["name:en"="Daejeon"]->.searchArea;
(
  nwr["tourism"="museum"](area.searchArea);
);
out geom;