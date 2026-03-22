[out:json][timeout:30];
area["name:en"="Kaohsiung"]->.searchArea;
(
  nwr["tourism"="museum"](area.searchArea);
);
out geom;