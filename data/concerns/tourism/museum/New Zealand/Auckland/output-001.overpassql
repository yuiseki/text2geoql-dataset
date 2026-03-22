[out:json][timeout:30];
area["name:en"="Auckland"]->.searchArea;
(
  nwr["tourism"="museum"](area.searchArea);
);
out geom;