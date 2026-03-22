[out:json][timeout:30];
area["name:en"="Kaohsiung"]->.searchArea;
(
  nwr["tourism"="hotel"](area.searchArea);
);
out geom;