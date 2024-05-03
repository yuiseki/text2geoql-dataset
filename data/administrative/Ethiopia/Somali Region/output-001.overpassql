[out:json][timeout:30000];
area["name:en"="Ethiopia"]->.searchArea;
(
  relation["boundary"="administrative"]["name:en"="Somali Region"](area.searchArea);
);
out geom;
